# Obsidian Notes Verify feature map

This directory maps the reader-visible parts of an Obsidian engineering reading note to ONV verification recipes.

## Baseline preconditions

- The verifier receives the exact Markdown note and its Obsidian vault root.
- `onv.py doctor` prints `ONV_DOCTOR_OK`.
- The note and attachments remain read-only during verification.
- Each run uses a new directory under `work/onv-runs/`.
- A multi-article Markdown file is narrowed with `--article NN`.

## Driving conventions

- Drive the artifact through its Obsidian wikilinks, not by passing a convenient PDF separately.
- Require both automated checks and visual attestation.
- Inspect the latest contact sheet after every source change.
- Do not reuse a pass when the note or PDF hash changes.
- Preserve all proof artifacts after cleanup.

## Proof and skip reporting

- A resolved PDF path proves the embed points to a real artifact.
- Extracted text proves content structure, not visual quality.
- Rendered pages prove the PDF can be opened, not that every page is readable.
- A visual reviewer must inspect every page and record pass or fail.
- Report unavailable source figures as a labeled teaching redraw; do not silently skip the framework.

## Features

- [Note structure](./note-structure.md) verifies the Markdown engineering record and attachment links.
- [ELI5 PDF](./eli5-pdf.md) verifies the two-panel teaching sequence and complete 10-page rhythm.
- [Framework data flow](./framework-dataflow.md) verifies framework provenance and input/operation/output/downstream.
- [Critical boundaries](./critical-boundaries.md) verifies evidence layers, shortcuts, decision boundaries, and migration tests.
