#!/usr/bin/env python3
"""Render and validate a rally review from a reviewed plan."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

from subtitle_evidence import EvidenceError, validate_evidence
from subtitle_layout import FrameSize, plan_caption


REQUIRED_CATEGORIES = {"core_technique", "improvable_rally", "highlight_point"}
EXPERTS = {
    "technique": "技术动作",
    "footwork_position": "步法站位",
    "tactics_shot_selection": "战术球路",
}
MAX_BYTES = 500_000_000
MIN_MARGIN = 0.5
OUTPUT_WIDTH = 2560
OUTPUT_HEIGHT = 1440
FONT_FILE = "/System/Library/Fonts/Supplemental/Songti.ttc"
RUN_LOG: Path | None = None


class ReviewError(Exception):
    """Raised when a plan or output fails a delivery gate."""


def expand_path(value: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(value))).resolve()


def run(args: list[str], *, input_text: str | None = None) -> str:
    result = subprocess.run(
        args, input=input_text, text=True, capture_output=True, check=False
    )
    if RUN_LOG is not None:
        RUN_LOG.parent.mkdir(parents=True, exist_ok=True)
        with RUN_LOG.open("a", encoding="utf-8") as log:
            log.write(f"$ {' '.join(args)}\n")
            if result.stderr:
                log.write(result.stderr)
            log.write(f"[exit {result.returncode}]\n")
    if result.returncode:
        detail = result.stderr[-2500:] or result.stdout[-2500:]
        raise ReviewError(
            f"Command failed ({result.returncode}): "
            f"{' '.join(args[:3])}\n{detail}"
        )
    return result.stdout


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise ReviewError(f"Required command not found: {name}")
    return path


def probe(path: Path) -> dict[str, Any]:
    ffprobe = require_tool("ffprobe")
    data = json.loads(
        run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_streams",
                "-show_format",
                "-of",
                "json",
                str(path),
            ]
        )
    )
    videos = [
        s for s in data.get("streams", []) if s.get("codec_type") == "video"
    ]
    audios = [
        s for s in data.get("streams", []) if s.get("codec_type") == "audio"
    ]
    if not videos:
        raise ReviewError(f"No video stream in {path}")
    video = videos[0]
    duration = float(data["format"]["duration"])
    video_duration = float(video.get("duration", duration))
    if duration <= 0:
        raise ReviewError(f"Invalid duration for {path}")
    if not math.isfinite(video_duration) or video_duration <= 0:
        raise ReviewError(f"Invalid video stream duration for {path}")
    return {
        "duration_s": duration,
        "video_duration_s": video_duration,
        "width": int(video["width"]),
        "height": int(video["height"]),
        "video_codec": video.get("codec_name"),
        "pixel_format": video.get("pix_fmt"),
        "color_primaries": video.get("color_primaries"),
        "color_transfer": video.get("color_transfer"),
        "color_space": video.get("color_space"),
        "has_audio": bool(audios),
    }


def probe_packet_spans(path: Path) -> list[tuple[float, float]]:
    """Read timestamps and packet durations without decoding video frames."""
    ffprobe = require_tool("ffprobe")
    raw = run(
        [
            ffprobe,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_packets",
            "-show_entries",
            "packet=pts_time,duration_time",
            "-of",
            "csv=p=0",
            str(path),
        ]
    )
    spans: list[tuple[float, float]] = []
    for line in raw.splitlines():
        columns = line.strip().split(",")
        if len(columns) < 2:
            continue
        try:
            pts, duration = float(columns[0]), float(columns[1])
        except ValueError:
            continue
        if math.isfinite(pts) and math.isfinite(duration) and duration > 0:
            spans.append((pts, duration))
    if not spans:
        raise ReviewError(f"No timestamped video packets in {path}")
    spans.sort()
    return spans


def _text(value: Any, field: str, max_length: int = 500) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ReviewError(f"{field} must be a non-empty string")
    value = value.strip()
    if len(value) > max_length:
        raise ReviewError(f"{field} is longer than {max_length} characters")
    return value


def validate_plan(
    plan: Any, source: Path, source_probe: dict[str, Any]
) -> list[dict[str, Any]]:
    if not isinstance(plan, dict) or plan.get("schema_version") != 1:
        raise ReviewError("Plan must be an object with schema_version 1")
    plan_source = expand_path(
        _text(plan.get("source_path"), "source_path", 1024)
    )
    if plan_source != source.resolve():
        raise ReviewError(
            f"Plan source_path {plan_source} does not match --source "
            f"{source.resolve()}"
        )
    recorded_duration = float(plan.get("source_duration_s", 0))
    source_duration = source_probe["duration_s"]
    if (
        recorded_duration <= 0
        or abs(recorded_duration - source_duration) > 0.25
    ):
        raise ReviewError(
            "Plan source_duration_s does not match the probed source"
        )
    _text(plan.get("focus"), "focus", 250)
    _text(plan.get("reference_comparison"), "reference_comparison", 4000)
    segments = plan.get("segments")
    if not isinstance(segments, list) or not 4 <= len(segments) <= 12:
        raise ReviewError("Plan must contain 4 to 12 whole-rally segments")
    categories: set[str] = set()
    validated: list[dict[str, Any]] = []
    previous_end = -1.0
    planned_duration = 0.0
    source_limit = min(120.0, source_duration * 0.25)
    for index, raw in enumerate(segments, 1):
        if not isinstance(raw, dict):
            raise ReviewError(f"Segment {index} must be an object")
        segment = dict(raw)
        segment["id"] = _text(segment.get("id"), f"segment {index} id", 64)
        category = segment.get("category")
        if category not in REQUIRED_CATEGORIES:
            raise ReviewError(
                f"Segment {segment['id']} has an invalid category"
            )
        categories.add(category)
        times = {}
        for key in ("start_s", "serve_contact_s", "dead_ball_s", "end_s"):
            try:
                times[key] = float(segment[key])
            except (KeyError, TypeError, ValueError) as exc:
                raise ReviewError(
                    f"Segment {segment['id']} has invalid {key}"
                ) from exc
            if not math.isfinite(times[key]):
                raise ReviewError(
                    f"Segment {segment['id']} has non-finite {key}"
                )
        start, serve, dead, end = (
            times[k]
            for k in ("start_s", "serve_contact_s", "dead_ball_s", "end_s")
        )
        if not (0 <= start < serve < dead < end <= source_duration):
            raise ReviewError(
                f"Segment {segment['id']} event times are not ordered "
                "inside the source"
            )
        if start < previous_end - 1e-6:
            raise ReviewError("Segments must be ordered and must not overlap")
        previous_end = end
        if serve - start < MIN_MARGIN or end - dead < MIN_MARGIN:
            raise ReviewError(
                f"Segment {segment['id']} has less than 0.5 seconds of "
                "planned rally padding"
            )
        segment.update(times)
        segment["verdict"] = segment.get("verdict")
        if segment["verdict"] not in {"good", "bad"}:
            raise ReviewError(
                f"Segment {segment['id']} verdict must be good or bad"
            )
        segment["reason"] = _text(
            segment.get("reason"), f"{segment['id']} reason", 1000
        )
        segment["drill"] = _text(
            segment.get("drill"), f"{segment['id']} drill", 1000
        )
        segment["subtitle"] = _text(
            segment.get("subtitle"), f"{segment['id']} subtitle", 48
        )
        if any(
            ch in segment["subtitle"] for ch in "'\\%[]\n\r"
        ):
            raise ReviewError(
                f"Segment {segment['id']} subtitle contains unsupported "
                "render characters"
            )
        experts = segment.get("experts")
        if not isinstance(experts, dict) or set(experts) != set(EXPERTS):
            raise ReviewError(
                f"Segment {segment['id']} must include exactly three "
                "independent expert findings"
            )
        normalized_experts = {}
        for expert in EXPERTS:
            finding = experts[expert]
            if not isinstance(finding, dict):
                raise ReviewError(
                    f"Segment {segment['id']} expert {expert} must be "
                    "an object"
                )
            at_s = float(finding.get("at_s", -1))
            if not start <= at_s <= end:
                raise ReviewError(
                    f"Segment {segment['id']} expert {expert} timestamp "
                    "falls outside the rally"
                )
            normalized_experts[expert] = {
                "at_s": at_s,
                "conclusion": _text(
                    finding.get("conclusion"),
                    f"{segment['id']} {expert} conclusion",
                    1000,
                ),
            }
        segment["experts"] = normalized_experts
        planned_duration += end - start
        validated.append(segment)
    missing = REQUIRED_CATEGORIES - categories
    if missing:
        raise ReviewError(
            f"Missing required categories: {', '.join(sorted(missing))}"
        )
    if planned_duration > source_limit + 1e-6:
        raise ReviewError(
            f"Planned runtime {planned_duration:.3f}s exceeds "
            f"{source_limit:.3f}s"
        )
    return validated


def validate_boundary_audit(
    segments: list[dict[str, Any]], source: Path, manifest_path: Path
) -> Path:
    manifest_path = manifest_path.expanduser().resolve()
    if not manifest_path.is_file():
        raise ReviewError(
            f"Boundary audit manifest is missing: {manifest_path}"
        )
    try:
        rows = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReviewError("Boundary audit manifest is invalid JSON") from exc
    if not isinstance(rows, list):
        raise ReviewError("Boundary audit manifest must be a JSON list")

    expected = {
        (segment["id"], event): float(segment[timestamp_field])
        for segment in segments
        for event, timestamp_field in (
            ("serve", "serve_contact_s"),
            ("dead_ball", "dead_ball_s"),
        )
    }
    verified: set[tuple[str, str]] = set()
    source_path = str(source.resolve())
    for row in rows:
        if not isinstance(row, dict) or row.get("source") != source_path:
            continue
        segment_id = row.get("segment")
        event = row.get("event")
        if (
            not isinstance(segment_id, str)
            or not isinstance(event, str)
            or event not in {"serve", "dead_ball"}
        ):
            continue
        key = (segment_id, event)
        if key not in expected:
            continue
        if key in verified:
            raise ReviewError(
                f"Duplicate boundary evidence for {key[0]} {key[1]}"
            )
        try:
            timestamp = float(row["timestamp_s"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ReviewError(f"Invalid boundary timestamp for {key}") from exc
        if not math.isclose(timestamp, expected[key], abs_tol=0.001):
            raise ReviewError(
                f"Stale boundary timestamp for {key[0]} {key[1]}"
            )
        if row.get("exit_code") != 0:
            raise ReviewError(f"Boundary frame extraction failed for {key}")
        review_status = str(row.get("visual_review", "")).strip()
        if review_status != "PASS" and not review_status.startswith("PASS:"):
            raise ReviewError(
                f"Boundary frames are not visually approved for {key}"
            )
        if (
            row.get("sample_rate_fps") != 8
            or row.get("window_duration_s") != 1.0
        ):
            raise ReviewError(
                f"Boundary evidence has the wrong sample window for {key}"
            )
        image_path = Path(str(row.get("image", ""))).expanduser()
        if not image_path.is_file():
            raise ReviewError(f"Boundary evidence image is missing for {key}")
        verified.add(key)

    missing = expected.keys() - verified
    if missing:
        segment, event = sorted(missing)[0]
        raise ReviewError(
            "Missing visually approved boundary evidence for "
            f"{segment} {event}"
        )
    return manifest_path


def validate_report(
    report: dict[str, Any],
    source_probe: dict[str, Any],
    video_probe: dict[str, Any],
    video_path: Path,
) -> None:
    segments = report.get("segments", [])
    categories = {s.get("category") for s in segments}
    if not 4 <= len(segments) <= 12 or categories != REQUIRED_CATEGORIES:
        raise ReviewError(
            "Stored report fails clip count or category coverage"
        )
    if any(
        float(s.get("pre_serve_margin_s", 0)) < MIN_MARGIN
        or float(s.get("post_dead_ball_margin_s", 0)) < MIN_MARGIN
        for s in segments
    ):
        raise ReviewError(
            "Stored report includes a rally margin below 0.5 seconds"
        )
    duration = float(video_probe["duration_s"])
    ratio = duration / float(source_probe["duration_s"])
    if duration > min(120.0, float(source_probe["duration_s"]) * 0.25) + 0.02:
        raise ReviewError("Encoded duration exceeds acceptance limit")
    if video_path.stat().st_size > MAX_BYTES:
        raise ReviewError("Encoded file exceeds 500 MB")
    if (
        video_probe["width"] < OUTPUT_WIDTH
        or video_probe["height"] < OUTPUT_HEIGHT
    ):
        raise ReviewError("Encoded dimensions are below 2K")
    if video_probe["video_codec"] != "h264" or any(
        video_probe.get(k) != "bt709"
        for k in ("color_primaries", "color_transfer", "color_space")
    ):
        raise ReviewError("Encoded codec or SDR BT.709 color tags failed")
    expected = report.get("render", {})
    if int(expected.get("clip_count", -1)) != len(segments):
        raise ReviewError("Reported clip count does not match the timeline")
    if set(expected.get("category_coverage", [])) != categories:
        raise ReviewError(
            "Reported category coverage does not match the timeline"
        )
    if abs(duration - float(expected.get("duration_s", -99))) > 0.03:
        raise ReviewError("Encoded duration does not match the stored report")
    if abs(ratio - float(expected.get("source_duration_ratio", -99))) > 0.001:
        raise ReviewError(
            "Encoded duration ratio does not match the stored report"
        )


def selected_packet_spans(
    spans: list[tuple[float, float]], start: float, end: float
) -> tuple[float, float, float]:
    selected = [
        (pts, duration)
        for pts, duration in spans
        if pts + 1e-7 >= start and pts < end - 1e-7
    ]
    if not selected:
        raise ReviewError(
            f"No source frames inside clip {start:.3f}–{end:.3f}s"
        )
    first = selected[0][0]
    last_end = selected[-1][0] + selected[-1][1]
    total_duration = sum(duration for _, duration in selected)
    return first, last_end, total_duration


def _escape_filter_text(text: str) -> str:
    return (
        text.replace("\\", r"\\")
        .replace(":", r"\:")
        .replace(",", r"\,")
        .replace("'", r"\'")
    )


def build_filter(segments: list[dict[str, Any]], has_audio: bool) -> str:
    filters: list[str] = []
    concat_inputs: list[str] = []
    for index, s in enumerate(segments):
        label = f"v{index}"
        caption_duration = float(
            s.get("source_frame_duration_s", s["end_s"] - s["start_s"])
        )
        caption = plan_caption(
            s["subtitle"],
            duration_s=caption_duration,
            frame=FrameSize(OUTPUT_WIDTH, OUTPUT_HEIGHT),
        )
        vchain = (
            f"[0:v:0]trim=start={s['start_s']:.6f}:end={s['end_s']:.6f},"
            "setpts=PTS-STARTPTS,"
            "zscale=transfer=linear:npl=100,format=gbrpf32le,"
            "tonemap=tonemap=hable:desat=0,"
            "zscale=primaries=bt709:transfer=bt709:matrix=bt709:range=tv,"
            f"scale={OUTPUT_WIDTH}:{OUTPUT_HEIGHT}:flags=lanczos,"
            "format=yuv420p"
        )
        for page in caption.pages:
            text = "\n".join(
                _escape_filter_text(line) for line in page.lines
            )
            vchain += (
                ",drawtext=text='"
                + text
                + f"':fontfile={FONT_FILE}:"
                + "fontcolor=white:"
                + f"fontsize={caption.style.font_size_px}:"
                + f"borderw={caption.style.outline_px}:bordercolor=black:"
                + "box=1:boxcolor=black@0.58:"
                + f"boxborderw={caption.style.box_padding_px}:"
                + "text_align=center:line_spacing=0:"
                + "x=(w-text_w)/2:"
                + f"y=h*{caption.style.center_y_fraction:.6f}-text_h/2:"
                + f"enable='gte(t,{page.start_s:.6f})*"
                + f"lt(t,{page.end_s:.6f})'"
            )
        vchain += (
            ",setsar=1,setparams=range=limited:color_primaries=bt709:"
            f"color_trc=bt709:colorspace=bt709[{label}]"
        )
        filters.append(vchain)
        concat_inputs.append(f"[{label}]")
        if has_audio:
            alabel = f"a{index}"
            filters.append(
                f"[0:a:0]atrim=start={s['start_s']:.6f}:end={s['end_s']:.6f},"
                f"asetpts=PTS-STARTPTS,aresample=48000[{alabel}]"
            )
            concat_inputs.append(f"[{alabel}]")
    audio_flag = 1 if has_audio else 0
    suffix = "[outv][outa]" if has_audio else "[outv]"
    filters.append(
        f"{''.join(concat_inputs)}concat=n={len(segments)}:"
        f"v=1:a={audio_flag}{suffix}"
    )
    return ";".join(filters)


def write_json(path: Path, value: Any) -> None:
    payload = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    temporary = path.with_name(path.name + ".pending")
    with temporary.open("x", encoding="utf-8") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def _timestamp(seconds: float) -> str:
    whole = int(seconds)
    millis = round((seconds - whole) * 1000)
    if millis == 1000:
        whole += 1
        millis = 0
    h, rem = divmod(whole, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}.{millis:03d}"


def build_timeline_markdown(
    source_path: str, segments: list[dict[str, Any]]
) -> str:
    lines = [
        f"# Rally timeline — {Path(source_path).name}",
        "",
        f"Source: `{source_path}`",
        "",
    ]
    for s in segments:
        lines.extend(
            [
                f"## {s['id']} — {s['category']} "
                f"({'做得好' if s['verdict'] == 'good' else '做得不好'})",
                "",
                f"- Clip: `{_timestamp(s['start_s'])}`–"
                f"`{_timestamp(s['end_s'])}`",
                f"- Serve contact: `{_timestamp(s['serve_contact_s'])}`; "
                f"pre-serve margin: **{s['pre_serve_margin_s']:.3f}s**",
                f"- Dead ball: `{_timestamp(s['dead_ball_s'])}`; "
                "post-dead-ball margin: "
                f"**{s['post_dead_ball_margin_s']:.3f}s**",
                f"- Reason: {s['reason']}",
                f"- Improvement drill: {s['drill']}",
                "- Expert findings:",
            ]
        )
        for expert, title in EXPERTS.items():
            finding = s["experts"][expert]
            lines.append(
                f"  - {title} at `{_timestamp(finding['at_s'])}`: "
                f"{finding['conclusion']}"
            )
        lines.append("")
    return "\n".join(lines)


def render(
    source: Path,
    plan_path: Path,
    output_dir: Path,
    *,
    check_only: bool = False,
    boundary_audit: Path | None = None,
    subtitle_evidence_manifest: Path | None = None,
) -> dict[str, Any]:
    source = source.resolve()
    plan_path = plan_path.resolve()
    if not source.is_file() or source.stem.upper() == "IMG_8677":
        raise ReviewError(
            f"Source is missing or explicitly excluded: {source}"
        )
    media = probe(source)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    segments = validate_plan(plan, source, media)
    frame_spans = probe_packet_spans(source)
    output_dir = output_dir.resolve()
    boundary_audit_path: Path | None = None
    if check_only:
        report_path = output_dir / "report.md"
        timeline_path = output_dir / "timeline.json"
        if not report_path.is_file() or not timeline_path.is_file():
            raise ReviewError(
                "--check requires report.md and timeline.json in an "
                "existing output directory"
            )
        report = json.loads(timeline_path.read_text(encoding="utf-8"))
        if report.get("qa", {}).get("status") != "PASS":
            raise ReviewError("Stored QA result is not PASS")
        audit_value = report.get("qa", {}).get("boundary_audit_manifest")
        if not isinstance(audit_value, str) or not audit_value:
            raise ReviewError(
                "Stored report is missing its boundary audit manifest"
            )
        boundary_audit_path = validate_boundary_audit(
            segments, source, expand_path(audit_value)
        )
        video = output_dir / "review.mp4"
        rendered = probe(video)
        validate_report(report, media, rendered, video)
        result = {
            "status": "PASS",
            "video": str(video),
            "duration_s": rendered["duration_s"],
        }
        if subtitle_evidence_manifest is not None:
            try:
                evidence = validate_evidence(
                    subtitle_evidence_manifest,
                    video,
                    duration_s=rendered["video_duration_s"],
                    width_px=rendered["width"],
                    height_px=rendered["height"],
                )
            except EvidenceError as exc:
                raise ReviewError(str(exc)) from exc
            result["subtitle_visual_review"] = "PASS"
            result["subtitle_sample_count"] = len(evidence["samples"])
        return result

    if boundary_audit is None:
        raise ReviewError(
            "Rendering requires --boundary-audit with a visually "
            "approved manifest"
        )
    boundary_audit_path = validate_boundary_audit(
        segments, source, boundary_audit
    )
    if output_dir.exists():
        raise ReviewError(
            "Output directory already exists; refusing to overwrite: "
            f"{output_dir}"
        )
    output_dir.mkdir(parents=True)
    ffmpeg = require_tool("ffmpeg")
    encoders = run([ffmpeg, "-hide_banner", "-encoders"])
    if "h264_videotoolbox" not in encoders:
        raise ReviewError("FFmpeg does not provide h264_videotoolbox")
    filters_available = run([ffmpeg, "-hide_banner", "-filters"])
    if (
        "zscale" not in filters_available
        or "tonemap" not in filters_available
        or "drawtext" not in filters_available
    ):
        raise ReviewError(
            "FFmpeg must provide zscale, tonemap, and drawtext filters"
        )
    if not Path(FONT_FILE).is_file():
        raise ReviewError(f"CJK subtitle font is not available: {FONT_FILE}")
    if (
        media["color_transfer"] not in {"arib-std-b67", "smpte2084"}
        or media["color_primaries"] != "bt2020"
    ):
        raise ReviewError(
            "This render path expects BT.2020 HLG or PQ source video"
        )
    for segment in segments:
        first, rendered_end, total_duration = selected_packet_spans(
            frame_spans, segment["start_s"], segment["end_s"]
        )
        # The one-frame deduction accounts for encoder/fps timestamp rounding.
        one_frame = 1.0 / 59.94
        segment["actual_first_frame_s"] = first
        segment["actual_video_end_s"] = rendered_end
        segment["pre_serve_margin_s"] = segment["serve_contact_s"] - first
        segment["post_dead_ball_margin_s"] = (
            rendered_end - segment["dead_ball_s"] - one_frame
        )
        segment["source_frame_duration_s"] = total_duration
        if (
            segment["pre_serve_margin_s"] < MIN_MARGIN
            or segment["post_dead_ball_margin_s"] < MIN_MARGIN
        ):
            raise ReviewError(
                f"{segment['id']} has less than 0.5 seconds of "
                "conservative rally padding"
            )

    planned_duration = sum(s["source_frame_duration_s"] for s in segments)
    limit = min(120.0, media["duration_s"] * 0.25)
    if planned_duration > limit + 1e-6:
        raise ReviewError(
            f"Selected whole rallies take {planned_duration:.3f}s; "
            f"limit is {limit:.3f}s"
        )

    video_path = output_dir / "review.mp4"
    filter_graph = build_filter(segments, media["has_audio"])
    command = [
        ffmpeg,
        "-hide_banner",
        "-nostdin",
        "-i",
        str(source),
        "-filter_complex",
        filter_graph,
        "-map",
        "[outv]",
    ]
    if media["has_audio"]:
        command.extend(["-map", "[outa]"])
    command.extend(
        [
            "-c:v",
            "h264_videotoolbox",
            "-allow_sw",
            "0",
            "-b:v",
            "14M",
            "-maxrate",
            "18M",
            "-bufsize",
            "28M",
            "-profile:v",
            "high",
            "-pix_fmt",
            "yuv420p",
            "-fps_mode",
            "vfr",
            "-color_primaries",
            "bt709",
            "-color_trc",
            "bt709",
            "-colorspace",
            "bt709",
            "-color_range",
            "tv",
        ]
    )
    if media["has_audio"]:
        command.extend(["-c:a", "aac", "-b:a", "160k"])
    command.extend(["-movflags", "+faststart", str(video_path)])
    run(command)
    output_probe = probe(video_path)
    output_bytes = video_path.stat().st_size
    source_ratio = output_probe["duration_s"] / media["duration_s"]
    actual_limit = min(120.0, media["duration_s"] * 0.25)
    if output_probe["duration_s"] > actual_limit + 0.02:
        raise ReviewError(
            f"Encoded duration {output_probe['duration_s']:.3f}s "
            f"exceeds {actual_limit:.3f}s"
        )
    if output_bytes > MAX_BYTES:
        raise ReviewError(
            f"Encoded MP4 is {output_bytes / 1_000_000:.1f} MB; "
            "limit is 500 MB"
        )
    if (
        output_probe["width"] < OUTPUT_WIDTH
        or output_probe["height"] < OUTPUT_HEIGHT
    ):
        raise ReviewError("Encoded resolution is below 2560×1440")
    if output_probe["video_codec"] != "h264":
        raise ReviewError(
            "Expected H.264 from VideoToolbox, found "
            f"{output_probe['video_codec']}"
        )
    if any(
        output_probe.get(k) != "bt709"
        for k in ("color_primaries", "color_transfer", "color_space")
    ):
        raise ReviewError("Output is not tagged BT.709 SDR")
    if not video_path.is_file() or not output_bytes:
        raise ReviewError("Encoded output is missing or empty")

    final = {
        "schema_version": 1,
        "source": {"path": str(source), **media},
        "focus": plan["focus"],
        "reference_comparison": plan["reference_comparison"],
        "segments": segments,
        "render": {
            "path": str(video_path),
            "duration_s": output_probe["duration_s"],
            "source_duration_ratio": source_ratio,
            "clip_count": len(segments),
            "category_coverage": sorted({s["category"] for s in segments}),
            "width": output_probe["width"],
            "height": output_probe["height"],
            "video_codec": output_probe["video_codec"],
            "color_primaries": output_probe["color_primaries"],
            "color_transfer": output_probe["color_transfer"],
            "color_space": output_probe["color_space"],
            "file_size_bytes": output_bytes,
            "encoding": "FFmpeg h264_videotoolbox",
        },
        "qa": {
            "status": "PASS",
            "checks": [
                "4–12 complete rallies",
                "all three categories covered",
                "serve and dead-ball margins >= 0.5s with "
                "one-frame conservatism",
                "rendered duration <= 120s and <= 25% of source",
                "VideoToolbox H.264, >=2560x1440, BT.709 SDR, <=500MB",
            ],
            "subtitle_visual_review": (
                "PENDING: inspect sample frames for every rendered video"
            ),
            "boundary_visual_review": (
                "PASS: each serve and dead-ball timestamp has approved "
                "8 fps source-frame evidence"
            ),
            "boundary_audit_manifest": str(boundary_audit_path),
            "remote_qa_bot": "NOT RUN",
        },
    }
    write_json(output_dir / "timeline.json", final)
    (output_dir / "timeline.md").write_text(
        build_timeline_markdown(str(source), segments), encoding="utf-8"
    )
    output_description = (
        f"{output_probe['width']}×{output_probe['height']} "
        f"{output_probe['video_codec']} "
        f"{output_probe['color_primaries']}/{output_probe['color_transfer']}/"
        f"{output_probe['color_space']}, {output_bytes / 1_000_000:.1f} MB"
    )
    report_lines = [
        f"# Badminton review report — {source.name}",
        "",
        f"- Source: `{source}`",
        f"- Source duration: {media['duration_s']:.3f}s",
        f"- Rendered duration: {output_probe['duration_s']:.3f}s "
        f"({source_ratio:.2%} of source)",
        f"- Clips: {len(segments)}",
        "- Category coverage: "
        f"{', '.join(sorted({s['category'] for s in segments}))}",
        f"- Video: `{video_path}`",
        f"- Output: {output_description}",
        "- Local render validation: PASS",
        "- Source boundary frame review: PASS",
        "- Visual subtitle inspection: pending",
        "- Remote QA bot: not run",
        "",
        "## Segment margins and findings",
        "",
        build_timeline_markdown(str(source), segments).split("\n", 4)[4],
        "## Reference comparison",
        "",
        plan["reference_comparison"],
        "",
        "## QA status",
        "",
        "This report records local automated media checks. It does not "
        "represent a remote QA bot result.",
    ]
    (output_dir / "report.md").write_text(
        "\n".join(report_lines).rstrip() + "\n", encoding="utf-8"
    )
    return {
        "status": "PASS",
        "source": str(source),
        "output": str(video_path),
        "duration_s": output_probe["duration_s"],
        "ratio": source_ratio,
        "clip_count": len(segments),
        "category_coverage": sorted({s["category"] for s in segments}),
        "file_size_bytes": output_bytes,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Source MOV or MP4")
    parser.add_argument("--plan", required=True, help="Reviewed timeline JSON")
    parser.add_argument(
        "--output-dir",
        required=True,
        help="New output directory for this review",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Recheck an existing report and MP4",
    )
    parser.add_argument(
        "--boundary-audit",
        help="Visually approved manifest from audit_rally_boundaries.py",
    )
    parser.add_argument(
        "--subtitle-evidence-manifest",
        help="Every-four-second subtitle evidence with PASS visual review",
    )
    parser.add_argument(
        "--log", help="Append FFmpeg/ffprobe output to this log file"
    )
    args = parser.parse_args(argv)
    try:
        global RUN_LOG
        RUN_LOG = expand_path(args.log) if args.log else None
        result = render(
            expand_path(args.source),
            expand_path(args.plan),
            expand_path(args.output_dir),
            check_only=args.check,
            boundary_audit=(
                expand_path(args.boundary_audit)
                if args.boundary_audit
                else None
            ),
            subtitle_evidence_manifest=(
                expand_path(args.subtitle_evidence_manifest)
                if args.subtitle_evidence_manifest
                else None
            ),
        )
    except (
        ReviewError,
        OSError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
