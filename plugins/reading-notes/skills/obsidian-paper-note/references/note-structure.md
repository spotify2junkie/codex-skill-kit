# Reading-note structure

Use this structure as an information contract, not as filler. Keep the paper's real terminology and adapt sections to the source.

## Entry and navigation

In standalone mode, start with compact YAML metadata for title, source, date, topic, and tags. In append mode, inherit the master note's metadata and begin with:

```markdown
## NN. Full paper title
```

Add source type, date, authors or organization, canonical URL or DOI, topic tags, and any ranking score the user supplied. Embed the PDF and one figure near the entry so the reader can inspect them without leaving the note.

## Required reasoning order

1. **一句话结论与洞见.** State what changes and its strongest evidence boundary. Add a few sentences explaining the distinctive insight or counterintuitive point in motivation, architecture or argument; do not manufacture novelty when none is demonstrated.
2. **主线图.** Show the core loop or pipeline in one compact diagram. Name fixed roles used in the ELI5 explanation.
3. **为什么和我有关.** Connect the source to the user's decision, work, interview preparation, or production system. Do not claim the user has built or shipped anything they have not.
4. **ELI5 与具体例子.** Use one concrete case with small, clearly labeled teaching values. Explain where the analogy stops matching the real system.
5. **架构与数据流.** Include the relevant original architecture figure when present, not only a link to the paper. Use stable module IDs across figure annotations, prose, I/O tables and PDF concept cards. For every material item, state `输入 → 操作 → 输出 → 下游`, including format/shape when disclosed, actual implementation and one connected example. Distinguish training/inference, features/labels, alternative branches and offline evaluation. If no figure exists, label the redraw and do not invent undisclosed internals.
6. **训练、Loss、Reward、Objective.** State training inputs/labels, each loss's operands and supervised module, weights, updated/frozen parameters, and gradient/reward paths. Explain what the main task objective is and what supports any claim of dominance. A large coefficient alone proves neither gradient dominance nor causal contribution; separate declared main loss, measured gradients and ablation evidence. Mark missing evidence undisclosed. For runtime/API material, describe execution objectives without inventing training losses.
7. **实验与指标.** Record dataset, time or random split, sample size, denominator, baseline, metric, variance or confidence interval, latency, and ablations when disclosed. Separate offline technical metrics from online business metrics.
8. **证据账本.** Use five explicit categories: source-supported calculation, author interpretation, local inference, unproved claim, and simpler baseline or shortcut.
9. **迁移到实际工作.** Write `可以复制`, `必须改变`, and `不能复制`. Add production authority boundaries, monitoring, rollback, and one smallest falsifiable experiment.
10. **学习路线与事实核对.** Give 3–4 stops with purpose, suggested time, and verified links. End with primary-source anchors precise enough to reproduce the note.

## Explanation rules

- Define each important term on first use.
- Put the conclusion before the formula. Then explain every symbol and identify whether a value is an input, label, learned parameter, sampled output, or post-processed score.
- Use tables for ledgers and exact mappings. Use diagrams only when the relationship is easier to see than to read.
- Do not reproduce hidden chain-of-thought. Summarize the source's stated rationale or expose auditable intermediate fields instead.
- A generated label and a thresholded business decision need different names when the source overloads notation.
- Naming two FC heads Intent/Packaging does not establish semantic disentanglement. Explain operations and imposed constraints first, then the authors' interpretation and what experiments do or do not establish. Apply this reasoning to other named modules without repeating the same anecdote in every note.
- Distinguish analogy from implementation. Each ELI5 explanation maps to a real module and its I/O; a child-friendly story must not invent sequential dependencies or erase permission/deletion boundaries.
