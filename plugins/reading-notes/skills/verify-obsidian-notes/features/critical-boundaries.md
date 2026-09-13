# Critical boundaries

Critical boundaries keep paper facts, author claims, missing evidence, and work-transfer ideas from collapsing into one confident story.

## Sub-features

- `critical-evidence-layers` separates calculation facts, author interpretation, and unproved claims.
- `critical-shortcut` records a simpler internal solution that could mimic the reported gain.
- `critical-decision-boundary` keeps enforcement behind rules or human review.
- `critical-migration-test` defines a small experiment that can fail.

## How to get to it (user POV)

- Open `Insight 与反直觉亮点` in the note.
- Read `证据与边界` and `事实核对`.
- Read the training ledger and metrics page in the PDF.
- Finish at `迁移到我的工作`.

## Driving it with ONV CLI

Preconditions:

- The note contains the full article section rather than a summary card.
- The PDF embed resolves and text extraction succeeds.

- **Verify evidence layers.** Require every `note.critical.*` check to pass.
- **Verify the production boundary.** Require `note.production_boundary` to identify both a consequential action and its rule or human-review gate.
- **Verify PDF evidence.** Require `pdf.evidence_boundary` on page 9 and `pdf.migration_route` on page 10.
- **Review meaning.** Confirm the prose does not equate metric gain with module semantics or business causality. Record a visual pass only after this content check.

## Gotchas

- `Deployed` does not prove incremental recall, loss reduction, or a controlled online gain.
- A single benchmark score does not prove the author's explanation of an internal representation.
- A generated risk candidate is not an enforcement fact.
- A migration idea without a locked holdout, replay, or failure condition is a proposal, not a test.
