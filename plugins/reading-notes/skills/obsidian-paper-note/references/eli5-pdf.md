# ELI5 PDF profile

Use this profile for the default embedded PDF. It specializes the adjacent `explain-eli5` skill for an Obsidian engineering note.

In this local-PDF mode, this profile overrides standalone explain-eli5 HTML/Sites publication and its 8–13-card default. Explicit user instructions still take precedence. Comics live in the PDF; technical architecture/I/O may also appear in Markdown. `主线图` means a compact technical flow diagram, not a standalone narrative 剧情主线 section.

## Page budget and compact layout

Default to at most ten A4 pages, including cover and references. Shorter PDFs are valid. Preserve architecture/I/O, implementation, training or runtime objective, evaluation, insight and evidence boundaries; shorten repetition rather than remove these. The ten-page layout below is a reference, not a quota. Choose the number of supported concept cards before rendering and record it in the manifest. Fewer cards/pages need no extra approval unless the user explicitly required exactly ten. This profile specializes the broader explain-eli5 concept-count default for compact engineering notes.

1. **Cover:** title, one-sentence conclusion, main flow, fixed characters, and color legend.
2. **Pages 2–6 in the ten-page layout:** ten supported concept cards, two per page; use fewer pages/cards for smaller sources. Each card is a two-panel comic with `烦恼` and `办法`. Its two takeaway lines are `解决了什么` and `代价是什么`. Put technical input/operation/output/downstream fields in a separate mapped strip or table, not extra takeaway lines. Dependency order must not imply a runtime chain between independent alternatives.
3. **Page 7:** framework and provenance. Show the source figure or a clearly labeled teaching redraw, followed by `输入 → 操作 → 输出 → 下游`.
4. **Page 8:** training ledger. Show SFT, RL, RLHF, GRPO, OPD, distillation, loss, reward, objective, updated parameters, frozen components, and gradient path only when the source supports them. Otherwise mark them not applicable or undisclosed.
5. **Page 9:** metrics and evidence. Include denominators, comparison baselines, evidence categories, critical boundaries, and the difference between technical and business results.
6. **Page 10:** production transfer, failure modes, smallest falsifiable experiment, guardrails or rollback, and a 3–4-stop learning route.

Do not invent weak concepts to reach ten cards. Cover each material architecture item through mapped cards or the I/O table, grouping related items explicitly. If the full required material genuinely cannot fit legibly within the agreed page budget, explain the tradeoff and ask about an appendix or increased budget instead of silently overflowing or shrinking text.

## Visual language

- Reuse one small cast throughout the PDF. For risk-control notes, typical roles are a user or seller, a risk analyst, the model or agent, and a human reviewer.
- Use notebook or graph-paper light styling and a blackboard dark HTML preview when HTML is part of the workflow. Print the PDF in a legible light theme.
- Use hand-drawn borders, restrained rotations, hard shadows, and inline SVG. Apply any turbulence filter to shapes only, never to text.
- Keep color semantics fixed: green means active, orange means new, blue means stored, and red dashed means rejected or released. Never rely on color alone.
- Keep each comic panel's explanatory text within 15 Chinese characters when possible. Never shrink text until it is technically present but unreadable.
- Mark teaching values as `示意值`. Paper numbers need their table, figure, equation, or page anchor.

## Provenance and verification

- Prefer a source-owned figure when it can be lawfully and accurately extracted. Otherwise create a teaching redraw and say so on the page.
- When the original has a relevant architecture figure, actually place it in the PDF and record its source/page or crop provenance. A sidecar asset alone is insufficient. Explain every material item through the same stable module IDs; enlarge, crop with labels, or split explanation across pages rather than shrinking an unreadable full figure.
- Generate the PDF from a reproducible source such as HTML or SVG. Keep filenames stable after review.
- Verify the actual A4 page count against the maximum, or an explicitly agreed exact count. Check both takeaway labels against the recorded card count. Use `--max-pdf-pages 10` for the default budget and the version-bound manifest from `batch-verification.md`; retain `--expected-pdf-pages 10 --expected-cards 10` for an exact-ten contract.
- Render every page. Inspect for clipping, overlap, missing glyphs, empty pages, illegible figures, and dense report-card regression.
- If an HTML version exists, inspect light and dark themes plus a narrow viewport. Do not claim visual QA without opening the rendered evidence.
- Bind review receipts to current render inputs and final PDF hashes. Parent source review covers claims and module semantics; visual review covers every final page, figure inclusion and readability. Neither replaces the other. For local-PDF requests, don't publish HTML/Sites as a side effect of using explain-eli5.
