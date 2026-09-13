# Note structure

Note structure is the engineering reading record a user opens in Obsidian, including its PDF and framework-image embeds.

## Sub-features

- `note-sections` checks the conclusion, flow, relevance, framework, evidence, migration, and fact-check sections.
- `note-pdf-link` resolves exactly one embedded article PDF.
- `note-figure-link` resolves a framework image with explicit provenance.
- `note-training-ledger` finds a training objective or an explicit no-training statement.

## How to get to it (user POV)

- Open the article note in Obsidian.
- If the note is a collection, open the numbered article heading.
- Expand the `ELI5 精读 PDF` callout.
- Open the framework image from `架构图与数据流`.

## Driving it with ONV CLI

Preconditions:

- Doctor passes for the exact note and vault root.
- A collection note is narrowed with `--article NN`.

- **Verify structure.** Run `python3 .agents/skills/verify-obsidian-notes/scripts/onv.py verify --note <note> --vault-root <vault> --article <NN> --expected-pages 10 --run-dir <run>`. The report passes every `note.*` check.
- **Confirm links.** Read `report.json`. `note.pdf_resolves` and `note.figure_resolves` pass, and the resolved files live inside the supplied vault.
- **Confirm provenance.** `note.figure_provenance` passes because the note says original figure, teaching redraw, or explicitly states that no verifiable original exists.
- **Proof.** Preserve the report, hashes, extracted PDF text, and render evidence in the run directory.

## Gotchas

- A normal `[[file.pdf]]` link is not an embedded reading surface; ONV requires `![[file.pdf]]`.
- Obsidian may resolve a basename by search. ONV fails ambiguous suffix matches rather than guessing.
- A heading alone can pass a weak keyword test. ONV also resolves attachments and checks the PDF itself.
- Do not require comic cards in Markdown; the PDF owns that teaching layer.
