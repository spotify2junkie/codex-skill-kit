---
name: badminton-video-review
description: Review badminton match footage, select complete rallies, and produce a short edited video with timestamped technical, footwork, and tactical findings. Use when the user requests badminton match review, rally highlights, or a coaching cut.
---

# Badminton Video Review

Create a complete-rally edit and a source-backed coaching report. Do not guess serve or dead-ball times from fixed-length windows. If the footage does not show a boundary clearly, inspect more frames or exclude that rally.

## Workflow

1. Read the user's acceptance criteria and any reference project first. The most recent explicit criteria take precedence. Keep source media local; do not upload it to external services.
2. Probe the video and review it from start to end. Use a coarse contact sheet to find rallies, then inspect each selected rally closely enough to locate first serve contact and the point-ending dead ball. For every final plan, create a 1-second, 8-fps contact sheet starting 0.75 seconds before each annotated serve and dead-ball timestamp. Use `scripts/audit_rally_boundaries.py` to create these sheets. Visually review every sheet against its source clip, then mark each manifest row `PASS`. The renderer rejects a missing, stale, incomplete, or unreviewed manifest. Treat a timestamp as a hypothesis until the frames show the event; correct it or exclude the rally when the event is unclear. Describe people by visible clothing or court position unless the user identifies them.
3. Select 4–12 whole rallies, with at least one `core_technique`, one `improvable_rally`, and one `highlight_point`. Keep each in/out around the full rally. The clip must begin at least 0.5 seconds before serve contact and end at least 0.5 seconds after the dead ball. If the runtime is too long, drop a whole lower-value rally and recheck category coverage. Never cut through an exchange.
4. For each rally, record `做得好` or `做得不好`, a visible reason, and a specific improvement drill. Independently review the same evidence through three lenses: technique, footwork and court position, and tactics/shot selection. Every finding needs its own source timestamp and visible evidence. Do not state that a human coach verified a conclusion unless they did.
5. Write a review JSON using the schema in `references/manifest-schema.md`. Keep the source path and all timestamps in source-relative seconds. Include concise Chinese subtitles. Leave `IMG_8677` out when working on the required test set.
6. Render with the packaged command. One invocation creates the video, JSON and Markdown timelines, and the report:

   Resolve `skill_dir` from this installed skill's actual location. Set `source`, `plan`, and `output_dir` to the current task's files; keep the output directory new.

   ```sh
   skill_dir="/absolute/path/to/installed/badminton-review/skills/badminton-video-review"
   plugin_root="$(cd "$skill_dir/../.." && pwd)"
   source="$HOME/path/to/match.MOV"
   plan="$HOME/path/to/review-plan.json"
   output_dir="$HOME/path/to/new-deliverables"
   boundary_audit="$HOME/path/to/reviewed-boundaries/manifest.json"
   python3 "$plugin_root/scripts/badminton_review.py" \
     --source "$source" \
     --plan "$plan" \
     --boundary-audit "$boundary_audit" \
     --output-dir "$output_dir"
   ```

   Use the same command for each approved input. Resolve paths from `$HOME` or `$OPS_ROOT`; do not put a machine-specific `/Users/...` path in packaged scripts or configuration.
7. Inspect rendered frames from every video. Confirm the subtitle sits in the horizontal center of the lower third, is legible, and does not cover a player's key action. Probe the final MP4 and run `--check` against its report. A render is not accepted if a quality gate fails.

## Required output

For each source, deliver `review.mp4`, `timeline.json`, `timeline.md`, and `report.md`. The report must give the source path, source and rendered duration, ratio, clip count, category coverage, actual pre-serve and post-dead-ball margins per clip, expert findings with timestamps, output resolution/codec/color/file size, and the reference comparison with its limits. Use the named comparison project only as an independent reference; the render helper does not depend on it.

Do not import into Photos unless the user explicitly authorizes that action. Keep large video artifacts out of git. Do not claim a remote QA bot passed unless that bot actually ran; record local validator results separately.

## Quality gates

See [the manifest schema](references/manifest-schema.md) and [render and evidence checks](references/quality-gates.md). If a whole-rally edit cannot satisfy the category, margin, duration, codec, color, resolution, or file-size limits, stop and report the exact failed gate. Do not silently relax a criterion.
