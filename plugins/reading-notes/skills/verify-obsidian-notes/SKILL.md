---
name: verify-obsidian-notes
description: "Verify an Obsidian technical reading note and its embedded ELI5 PDF when structure, framework data flow, critical evidence boundaries, and rendered layout must be proven."
---

# Verify Obsidian Notes

ONV verifies the artifact the reader actually opens: an Obsidian Markdown note, its embedded PDF, and the framework image referenced by the note. It is read-only toward the note and attachments. A run writes only to its dedicated evidence directory.

Read [references/verification-contract.md](references/verification-contract.md) before changing the checks or interpreting a failure. Read the matching file under [features/](features/README.md) when verifying one part of the note.

## Launch

Resolve `skill_dir` from this installed skill's actual location; do not assume the old workspace's `.agents/skills` layout.

ONV is a short-lived CLI, so it has no server and does not launch or modify the Obsidian app. Start a run with an isolated directory:

```bash
skill_dir="/absolute/path/to/installed/reading-notes/skills/verify-obsidian-notes"
run_dir="work/onv-runs/$(date +%Y%m%d-%H%M%S)"
python3 "$skill_dir/scripts/onv.py" doctor \
  --note "/absolute/path/to/note.md" \
  --vault-root "/absolute/path/to/Obsidian vault"
```

The doctor is ready when it prints `ONV_DOCTOR_OK`. No authentication, port, seed data, or background process is used. Concurrent runs are safe only when they use different `run_dir` values.

## Doctor

Run doctor before every verification. It checks the exact note, vault root, Python version, and the installed Poppler/ImageMagick commands used by the verifier. Do not continue if the note is outside the supplied vault root or a required command is missing.

## Drive

Run the verifier against one article. Use `--article 01` when a Markdown file contains several numbered articles; omit it for a one-article note.

```bash
python3 "$skill_dir/scripts/onv.py" verify \
  --note "/absolute/path/to/note.md" \
  --vault-root "/absolute/path/to/Obsidian vault" \
  --article 01 \
  --expected-pages 10 \
  --run-dir "$run_dir"
```

This resolves the real Obsidian wikilinks, reads the embedded PDF, renders every page, and writes an automated report. An automated pass is not a final pass.

Open the generated `evidence/contact-sheet.png` with the available image-viewing tool. Inspect every page for clipping, overlap, missing glyphs, unreadable figures, weak hierarchy, inconsistent page numbers, and a layout that has collapsed back into dense report cards. Then record the observation:

```bash
python3 "$skill_dir/scripts/onv.py" attest \
  --run-dir "$run_dir" \
  --status pass \
  --reviewer "Codex visual review" \
  --comment "All pages readable; no clipping, overlap, or missing framework labels."

python3 "$skill_dir/scripts/onv.py" status --run-dir "$run_dir"
```

Only `ONV_PASS` with exit code `0` proves the note. Fix the source artifact and create a new run if either automated or visual checks fail.

## Evidence

Each run preserves:

- `report.json` and `report.md`, including the note/PDF hashes and every check;
- `evidence/pdf.txt`, the page-preserving text extraction;
- `evidence/page-*.png`, one image per PDF page;
- `evidence/contact-sheet.png`, the complete visual review surface;
- `visual-review.json`, the explicit visual attestation;
- `transcript.txt`, the exact verifier invocation and result.

Proof must use the real note and embedded PDF. A screenshot without link resolution and text checks is insufficient. Text checks without the rendered contact sheet are also insufficient. Never infer content from a filename or trust a prior run after the note or PDF hash changes.

## Cleanup

ONV starts no process. Cleanup removes only scratch files created inside that run and preserves all proof artifacts:

```bash
python3 "$skill_dir/scripts/onv.py" cleanup --run-dir "$run_dir"
python3 "$skill_dir/scripts/onv.py" status --run-dir "$run_dir"
```

Never delete or rewrite the source note, PDF, framework image, Obsidian configuration, or another run directory during cleanup.

## Helpers

`scripts/onv.py` is the only helper. Its commands are `doctor`, `verify`, `attest`, `status`, and `cleanup`. Run `python3 scripts/onv.py --help` for argument details. The script uses only Python's standard library plus `pdfinfo`, `pdftotext`, `pdftoppm`, and `magick` found by doctor.
