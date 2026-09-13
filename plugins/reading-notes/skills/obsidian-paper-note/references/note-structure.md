# Reading-note structure

Use this structure as an information contract, not as filler. Keep the paper's real terminology and adapt sections to the source.

## Entry and navigation

In standalone mode, start with compact YAML metadata for title, source, date, topic, and tags. In append mode, inherit the master note's metadata and begin with:

```markdown
## NN. Full paper title
```

Add source type, date, authors or organization, canonical URL or DOI, topic tags, and any ranking score the user supplied. Embed the PDF and one figure near the entry so the reader can inspect them without leaving the note.

## Required reasoning order

1. **一句话结论.** State what the method changes and the strongest evidence boundary in the same paragraph.
2. **主线图.** Show the core loop or pipeline in one compact diagram. Name fixed roles used in the ELI5 explanation.
3. **为什么和我有关.** Connect the source to the user's decision, work, interview preparation, or production system. Do not claim the user has built or shipped anything they have not.
4. **ELI5 与具体例子.** Use one concrete case with small, clearly labeled teaching values. Explain where the analogy stops matching the real system.
5. **架构与数据流.** For every material module, state `输入 → 操作 → 输出 → 下游`. Distinguish training-time inputs from inference-time inputs and labels from features.
6. **训练、Loss、Reward、Objective.** State what updates, what stays frozen, where gradients or rewards flow, and which details are undisclosed. If the source has no training, say so and describe the execution or evaluation objective instead.
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
