# ELI5 PDF profile

Use this profile for the default embedded PDF. It specializes the adjacent `explain-eli5` skill for an Obsidian engineering note.

## Ten-page contract

1. **Cover:** title, one-sentence conclusion, main flow, fixed characters, and color legend.
2. **Pages 2–6:** exactly ten dependency-ordered concept cards, two per page. Each card is a two-panel comic. The left panel is `烦恼`; the right panel is `办法`. Beneath it, write exactly two lines: `解决了什么` and `代价是什么`.
3. **Page 7:** framework and provenance. Show the source figure or a clearly labeled teaching redraw, followed by `输入 → 操作 → 输出 → 下游`.
4. **Page 8:** training ledger. Show SFT, RL, RLHF, GRPO, OPD, distillation, loss, reward, objective, updated parameters, frozen components, and gradient path only when the source supports them. Otherwise mark them not applicable or undisclosed.
5. **Page 9:** metrics and evidence. Include denominators, comparison baselines, evidence categories, critical boundaries, and the difference between technical and business results.
6. **Page 10:** production transfer, failure modes, smallest falsifiable experiment, guardrails or rollback, and a 3–4-stop learning route.

Do not invent weak concepts to reach ten cards. If the source genuinely cannot support the contract, preserve accuracy, explain the limitation, and ask whether the user prefers a shorter PDF.

## Visual language

- Reuse one small cast throughout the PDF. For risk-control notes, typical roles are a user or seller, a risk analyst, the model or agent, and a human reviewer.
- Use notebook or graph-paper light styling and a blackboard dark HTML preview when HTML is part of the workflow. Print the PDF in a legible light theme.
- Use hand-drawn borders, restrained rotations, hard shadows, and inline SVG. Apply any turbulence filter to shapes only, never to text.
- Keep color semantics fixed: green means active, orange means new, blue means stored, and red dashed means rejected or released. Never rely on color alone.
- Keep each comic panel's explanatory text within 15 Chinese characters when possible. Never shrink text until it is technically present but unreadable.
- Mark teaching values as `示意值`. Paper numbers need their table, figure, equation, or page anchor.

## Provenance and verification

- Prefer a source-owned figure when it can be lawfully and accurately extracted. Otherwise create a teaching redraw and say so on the page.
- Generate the PDF from a reproducible source such as HTML or SVG. Keep filenames stable after review.
- Verify exactly ten A4 pages, the ten-card count, and the ten occurrences of both required takeaway labels.
- Render every page. Inspect for clipping, overlap, missing glyphs, empty pages, illegible figures, and dense report-card regression.
- If an HTML version exists, inspect light and dark themes plus a narrow viewport. Do not claim visual QA without opening the rendered evidence.
