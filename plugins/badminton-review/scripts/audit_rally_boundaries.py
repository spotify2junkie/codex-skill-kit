#!/usr/bin/env python3
"""Extract visual evidence windows for planned serve and dead-ball events."""

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any


def boundary_events(plan: dict[str, Any]) -> list[dict[str, Any]]:
    """Return one serve and one dead-ball evidence request per rally."""
    events = []
    for segment in plan["segments"]:
        for kind, field in (
            ("serve", "serve_contact_s"),
            ("dead_ball", "dead_ball_s"),
        ):
            timestamp = float(segment[field])
            events.append(
                {
                    "segment": segment["id"],
                    "event": kind,
                    "timestamp_s": timestamp,
                    "window_start_s": max(0.0, timestamp - 0.75),
                }
            )
    return events


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.expanduser().resolve()
    plan_path = args.plan.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    if not source.is_file():
        parser.error(f"source does not exist: {source}")
    if output_dir.exists():
        parser.error(f"output directory already exists: {output_dir}")
    output_dir.mkdir(parents=True)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    rows = []
    for event in boundary_events(plan):
        stem = (
            f"{event['segment']}-{event['event']}-"
            f"{event['timestamp_s']:.3f}"
        )
        image_path = output_dir / f"{stem}.jpg"
        log_path = output_dir / f"{stem}.log"
        command = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            f"{event['window_start_s']:.3f}",
            "-i",
            str(source),
            "-t",
            "1.0",
            "-vf",
            "fps=8,crop=2000:1000:300:450,scale=960:-2,tile=2x4",
            "-frames:v",
            "1",
            str(image_path),
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        log_path.write_text(
            "$ "
            + " ".join(command)
            + "\n"
            + result.stdout
            + result.stderr
            + f"[exit {result.returncode}]\n",
            encoding="utf-8",
        )
        rows.append(
            {
                **event,
                "source": str(source),
                "plan": str(plan_path),
                "image": str(image_path),
                "log": str(log_path),
                "exit_code": result.returncode,
                "sample_rate_fps": 8,
                "window_duration_s": 1.0,
                "visual_review": "PENDING",
            }
        )
        if result.returncode:
            raise RuntimeError(f"ffmpeg failed for {stem}: {result.stderr}")
    (output_dir / "manifest.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"created {len(rows)} boundary sheets in {output_dir}")
    print(f"manifest: {output_dir / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
