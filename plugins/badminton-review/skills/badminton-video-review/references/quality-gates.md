# Render and evidence checks

## Rally boundaries

- Review the serve and point-ending moments at source resolution.
- Record the first serve contact and the point-ending dead-ball time as separate events.
- Calculate margins from the source frame timestamps selected by FFmpeg, allowing one output frame of conservative uncertainty.
- Require both margins to remain at least 0.5 seconds after that allowance. Never alter a clip boundary to hide a failed margin; re-review or drop the entire rally.
- At least four complete clips must remain, and all three categories must be represented.
- The planned and probed output durations must both be no greater than `min(120 seconds, 25% of source duration)`.

## Encoded output

- Use H.264 `h264_videotoolbox`, 2560×1440 or greater, and BT.709 SDR metadata after HLG tone mapping.
- Use only the primary video and audio streams. Ignore auxiliary and data streams.
- Render subtitles at a fixed size of at least 5.2% of frame height. The packaged layout uses 7% of frame height so the visible Songti glyphs can clear the 5.2% requirement. Do not shrink text to fit.
- Center the subtitle block horizontally and place its center between 82% and 90% of frame height. Include outline and box padding in the geometry check, and leave at least 5% of frame height below the block.
- Use white text with an opaque black outline of at least 3 px and a translucent black box. Keep each page to at most two lines and each line to at most 18 Unicode code points. Split longer subtitles across timed pages; keep the same font size on every page.
- Use `scripts/subtitle_evidence.py` to extract matching FFmpeg frames from the old and new MP4s at 0, 4, 8, ... seconds strictly below the video stream duration. Review every full-resolution `after-*.jpg` and mark each manifest row `visual_review` as `PASS` only after it passes. The tool also writes side-by-side comparison images with the old frame on the left and the new frame on the right. Then run `badminton_review.py --check --subtitle-evidence-manifest <manifest.json>` to require a complete, reviewed sample set.
- Inspect rendered frames for every video and confirm the subtitle does not cover a player's key action. A render is not accepted if a geometry, visibility, or subtitle evidence gate fails.
- Require the final MP4 to stay at or below 500 MB. Fail if VideoToolbox or the required tone-mapping filters are unavailable; do not substitute software encoding silently.

## Report and comparison

- Report source path, source duration, output duration, output/source ratio, clip count, category coverage, each rally's event timestamps and measured margins, three expert findings, codec, resolution, SDR color tags, and file size.
- Write the JSON timeline, Markdown timeline, and report only after the final media probes pass. Do not overwrite an existing output directory.
- Compare the reviewed video and its coaching evidence against the named reference project's documented report shape. If its runtime was not actually run on that same source, label the comparison as a documented-workflow comparison, not as an output-to-output execution.
- Record local QA separately from a remote QA bot. Never claim the remote bot passed unless its result is available.
