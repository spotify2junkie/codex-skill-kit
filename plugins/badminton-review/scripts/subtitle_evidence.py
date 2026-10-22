"""Create and validate FFmpeg-based subtitle frame review evidence."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Any


DEFAULT_INTERVAL_S = 4.0


class EvidenceError(Exception):
    """Raised when subtitle evidence is incomplete or invalid."""


def expand_path(value: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(value))).resolve()


def sample_timestamps(duration_s: float, interval_s: float) -> list[float]:
    if not math.isfinite(duration_s) or duration_s <= 0:
        raise EvidenceError("video duration must be finite and positive")
    if not math.isfinite(interval_s) or interval_s <= 0:
        raise EvidenceError("sample interval must be finite and positive")
    count = math.ceil((duration_s - 1e-9) / interval_s)
    return [round(index * interval_s, 6) for index in range(count)]


def _run(command: list[str], log_path: Path) -> str:
    result = subprocess.run(
        command, capture_output=True, text=True, check=False
    )
    with log_path.open("a", encoding="utf-8") as log:
        log.write(f"$ {shlex.join(command)}\n")
        if result.stdout:
            log.write(result.stdout)
        if result.stderr:
            log.write(result.stderr)
        log.write(f"[exit {result.returncode}]\n")
    if result.returncode:
        detail = result.stderr[-2000:] or result.stdout[-2000:]
        raise EvidenceError(
            f"Command failed ({result.returncode}): "
            f"{shlex.join(command[:4])}\n"
            f"{detail}"
        )
    return result.stdout


def probe_video(path: Path, log_path: Path) -> tuple[float, float, int, int]:
    output = _run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_type,width,height,duration",
            "-of",
            "json",
            str(path),
        ],
        log_path,
    )
    try:
        data = json.loads(output)
        format_duration = float(data["format"]["duration"])
        video = next(
            row for row in data["streams"] if row.get("codec_type") == "video"
        )
        video_duration = float(video.get("duration", format_duration))
        width = int(video["width"])
        height = int(video["height"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise EvidenceError(f"Cannot read video metadata from {path}") from exc
    except StopIteration as exc:
        raise EvidenceError(f"No video stream in {path}") from exc
    if (
        not math.isfinite(format_duration)
        or format_duration <= 0
        or not math.isfinite(video_duration)
        or video_duration <= 0
    ):
        raise EvidenceError(f"Invalid video duration for {path}")
    if width <= 0 or height <= 0:
        raise EvidenceError(f"Invalid video dimensions for {path}")
    return format_duration, video_duration, width, height


def _sample_frame(
    video: Path,
    timestamp_s: float,
    image: Path,
    log_path: Path,
) -> None:
    _run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-n",
            "-ss",
            f"{timestamp_s:.6f}",
            "-i",
            str(video),
            "-map",
            "0:v:0",
            "-frames:v",
            "1",
            "-q:v",
            "2",
            "-update",
            "1",
            str(image),
        ],
        log_path,
    )
    if not image.is_file() or image.stat().st_size == 0:
        raise EvidenceError(f"FFmpeg did not produce {image}")


def _make_comparison(
    before_image: Path,
    after_image: Path,
    output_image: Path,
    log_path: Path,
) -> None:
    _run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-n",
            "-i",
            str(before_image),
            "-i",
            str(after_image),
            "-filter_complex",
            "[0:v][1:v]hstack=inputs=2:shortest=1[outv]",
            "-map",
            "[outv]",
            "-frames:v",
            "1",
            "-q:v",
            "2",
            "-update",
            "1",
            str(output_image),
        ],
        log_path,
    )
    if not output_image.is_file() or output_image.stat().st_size == 0:
        raise EvidenceError(f"FFmpeg did not produce {output_image}")


def _make_contact_sheets(
    output_dir: Path,
    input_pattern: str,
    output_pattern: str,
    *,
    scaled_width_px: int,
    log_path: Path,
) -> list[Path]:
    output_glob = output_dir / output_pattern.replace("%02d", "*")
    _run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-n",
            "-pattern_type",
            "glob",
            "-framerate",
            "1",
            "-i",
            str(output_dir / input_pattern),
            "-vf",
            f"scale={scaled_width_px}:-1,tile=2x2",
            "-q:v",
            "2",
            str(output_dir / output_pattern),
        ],
        log_path,
    )
    sheets = sorted(output_dir.glob(output_glob.name))
    if not sheets or any(path.stat().st_size == 0 for path in sheets):
        raise EvidenceError(f"FFmpeg did not produce {output_pattern}")
    return sheets


def create_evidence(
    before_video: Path,
    after_video: Path,
    output_dir: Path,
    *,
    interval_s: float = DEFAULT_INTERVAL_S,
) -> Path:
    before_video = before_video.expanduser().resolve()
    after_video = after_video.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()
    if not before_video.is_file() or not after_video.is_file():
        raise EvidenceError("before and after videos must both exist")
    if output_dir.exists():
        raise EvidenceError(
            f"Output directory already exists; refusing to overwrite: "
            f"{output_dir}"
        )
    output_dir.mkdir(parents=True)
    log_path = output_dir / "commands.log"
    (
        before_format_duration,
        before_duration,
        before_width,
        before_height,
    ) = probe_video(before_video, log_path)
    (
        after_format_duration,
        after_duration,
        after_width,
        after_height,
    ) = probe_video(after_video, log_path)
    if (before_width, before_height) != (after_width, after_height):
        raise EvidenceError("before and after video dimensions do not match")
    timestamps = sample_timestamps(after_duration, interval_s)
    if timestamps[-1] >= before_duration:
        raise EvidenceError(
            "before video is shorter than the final after-video sample"
        )

    samples: list[dict[str, Any]] = []
    for index, timestamp in enumerate(timestamps):
        stem = f"sample-{index:03d}-t{timestamp:09.3f}s"
        before_image = output_dir / f"before-{stem}.jpg"
        after_image = output_dir / f"after-{stem}.jpg"
        comparison_image = output_dir / f"comparison-{stem}.jpg"
        _sample_frame(before_video, timestamp, before_image, log_path)
        _sample_frame(after_video, timestamp, after_image, log_path)
        _make_comparison(
            before_image, after_image, comparison_image, log_path
        )
        samples.append(
            {
                "timestamp_s": timestamp,
                "before_image": str(before_image),
                "after_image": str(after_image),
                "comparison_image": str(comparison_image),
                "exit_code": 0,
                "visual_review": "PENDING",
            }
        )

    after_contact_sheets = _make_contact_sheets(
        output_dir,
        "after-sample-*.jpg",
        "after-contact-%02d.jpg",
        scaled_width_px=1280,
        log_path=log_path,
    )
    comparison_contact_sheets = _make_contact_sheets(
        output_dir,
        "comparison-sample-*.jpg",
        "comparison-contact-%02d.jpg",
        scaled_width_px=1280,
        log_path=log_path,
    )
    manifest = {
        "schema_version": 1,
        "before_video": str(before_video),
        "after_video": str(after_video),
        "before_format_duration_s": before_format_duration,
        "before_video_duration_s": before_duration,
        "after_format_duration_s": after_format_duration,
        "after_video_duration_s": after_duration,
        "interval_s": interval_s,
        "sample_width_px": after_width,
        "sample_height_px": after_height,
        "comparison_order": "before on the left; after on the right",
        "after_contact_sheets": [str(path) for path in after_contact_sheets],
        "comparison_contact_sheets": [
            str(path) for path in comparison_contact_sheets
        ],
        "samples": samples,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def validate_evidence(
    manifest_path: Path,
    after_video: Path,
    *,
    duration_s: float,
    width_px: int,
    height_px: int,
    interval_s: float = DEFAULT_INTERVAL_S,
) -> dict[str, Any]:
    manifest_path = manifest_path.expanduser().resolve()
    after_video = after_video.expanduser().resolve()
    if not manifest_path.is_file():
        raise EvidenceError(
            "Subtitle evidence manifest is missing: "
            f"{manifest_path}"
        )
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EvidenceError(
            "Subtitle evidence manifest is invalid JSON"
        ) from exc
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise EvidenceError("Subtitle evidence manifest has an invalid schema")
    if Path(str(manifest.get("after_video", ""))).resolve() != after_video:
        raise EvidenceError(
            "Subtitle evidence refers to a different after video"
        )
    before_video = Path(str(manifest.get("before_video", ""))).expanduser()
    if not before_video.is_file():
        raise EvidenceError("Subtitle evidence before video is missing")
    if not math.isclose(
        float(manifest.get("interval_s", -1)), interval_s, abs_tol=1e-9
    ):
        raise EvidenceError("Subtitle evidence has the wrong sample interval")
    if not math.isclose(
        float(manifest.get("after_video_duration_s", -1)),
        duration_s,
        abs_tol=0.05,
    ):
        raise EvidenceError("Subtitle evidence duration does not match output")
    if (
        manifest.get("sample_width_px") != width_px
        or manifest.get("sample_height_px") != height_px
    ):
        raise EvidenceError("Subtitle samples do not match output dimensions")
    samples = manifest.get("samples")
    expected_timestamps = sample_timestamps(duration_s, interval_s)
    if (
        not isinstance(samples, list)
        or len(samples) != len(expected_timestamps)
    ):
        raise EvidenceError("Subtitle evidence has an incomplete sample set")
    for row, expected_time in zip(samples, expected_timestamps):
        if not isinstance(row, dict):
            raise EvidenceError("Subtitle evidence has an invalid sample row")
        try:
            timestamp = float(row["timestamp_s"])
        except (KeyError, TypeError, ValueError) as exc:
            raise EvidenceError(
                "Subtitle sample timestamp is invalid"
            ) from exc
        if not math.isclose(timestamp, expected_time, abs_tol=0.001):
            raise EvidenceError("Subtitle evidence has a missing sample time")
        if row.get("exit_code") != 0:
            raise EvidenceError("Subtitle sample extraction failed")
        review = str(row.get("visual_review", "")).strip()
        if review != "PASS" and not review.startswith("PASS:"):
            raise EvidenceError("Subtitle sample has not passed visual review")
        for key in ("before_image", "after_image", "comparison_image"):
            image_path = Path(str(row.get(key, ""))).expanduser()
            if not image_path.is_file():
                raise EvidenceError(
                    f"Subtitle evidence image is missing: {key}"
                )
    for key in ("after_contact_sheets", "comparison_contact_sheets"):
        sheets = manifest.get(key)
        if not isinstance(sheets, list) or not sheets:
            raise EvidenceError(f"Subtitle evidence is missing {key}")
        if any(
            not Path(str(path)).expanduser().is_file() for path in sheets
        ):
            raise EvidenceError(f"Subtitle evidence has a missing {key} file")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True, help="Existing fix1 MP4")
    parser.add_argument("--after", required=True, help="Newly rendered MP4")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--interval-s", type=float, default=DEFAULT_INTERVAL_S
    )
    args = parser.parse_args(argv)
    try:
        manifest = create_evidence(
            expand_path(args.before),
            expand_path(args.after),
            expand_path(args.output_dir),
            interval_s=args.interval_s,
        )
    except (EvidenceError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
