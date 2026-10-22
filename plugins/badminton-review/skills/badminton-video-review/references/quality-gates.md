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
- Use a readable subtitle centered horizontally in the lower third. Inspect a rendered frame during each clip; move or shorten text if it covers a key action, while keeping it in the lower third.
- Require the final MP4 to stay at or below 500 MB. Fail if VideoToolbox or the required tone-mapping filters are unavailable; do not substitute software encoding silently.

## Report and comparison

- Report source path, source duration, output duration, output/source ratio, clip count, category coverage, each rally's event timestamps and measured margins, three expert findings, codec, resolution, SDR color tags, and file size.
- Write the JSON timeline, Markdown timeline, and report only after the final media probes pass. Do not overwrite an existing output directory.
- Compare the reviewed video and its coaching evidence against the named reference project's documented report shape. If its runtime was not actually run on that same source, label the comparison as a documented-workflow comparison, not as an output-to-output execution.
- Record local QA separately from a remote QA bot. Never claim the remote bot passed unless its result is available.
