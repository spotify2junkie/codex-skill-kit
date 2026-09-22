# Recall and handoff record

Keep one topic-level record plus per-source evidence. Record observable actions and decisions, not hidden model reasoning. Use supported history APIs or supplied history; never scrape private transcript stores.

## Durable state

Use stable source IDs independent of rank. Keep selection and artifact records separate:

`candidate → source-verified → review-qualified → selected/confirmed → author-ready → rendered → source-reviewed + visually-reviewed → merged → delivered`

These are evidence-backed states, not a queue advancing with elapsed time. Missing text, disputes or changed inputs may stop/invalidate later states. Search and production have different completion predicates. Idle workers do not mean delivery.

For each source keep snapshots/versions, author paths, render-input hashes, PDF hash, report paths/hashes and unresolved issues. Keep a current pointer plus superseded versions. When content, diagrams or renderer change, mark dependent PDFs/reviews stale until renewed. A refreshed receipt cannot conceal unresolved findings in its report.

Record failures as symptom, cause, affected source/version, fix, recheck evidence and preventive check. Demonstrated patterns include wrong PDF identity, arithmetic errors, invented anchors, wrong arrows, module-ID drift, missing original figure, unreadable SVG, comic overlap, stale outputs and overstated deletion/security guarantees. Keep logs specific; do not copy all historical cases into every article.

## Collapsed master-note appendix

For authorized combined-note production, use one appendix with separate rows or subsections for each topic when several topics share a master. Each topic records current source and visual acceptance separately from merge/delivery:

```markdown
> [!info]- 搜索与制作记录
> 主题与用途：…
> 搜索范围与日期：…
> 候选数 / 去重后 / 合格数 / 确认精读数：…
> 评分、独立 Review 与名单确认：…
> 范围变更：…
> 当前进度：已制作…；当前原文/机制验收…；当前逐页视觉验收…；已合并…；已交付…
> 原文、图、PDF 与审查证据：[[附件/…/记录]]
> 实际失败与修复：…
> 最后验证时间、不可用检查、下一步：…
```

Use actual values or “未记录”, not invented counts. Article evidence stays near its article, detailed reports in attachments/work. No extra per-paper top-level Recall notes unless requested. A shortlist-only response may give this record in chat/work without writing Obsidian.

## Resume and scope changes

Read confirmed scope first, then current files and current-version reports. History proves prior decisions, not file existence. Check the vault and actual output paths before reporting “done”. If unavailable, retain local work and mark delivery unverified; do not relocate the vault or overwrite another copy automatically.

If 50 becomes 20, stop unstarted out-of-scope work, reconcile active workers through supported controls and retain already-created extras without deleting them unless authorized. Do not rerank the retained 20. Report retained/stopped work and already-published extras. Keep concurrency within runtime/memory capacity and close finished workers as required.

Final handoff names the master, accepted article/PDF counts, skipped/blocked items, coverage, unresolved issues and limits such as native UI/iCloud not tested. Distinguish historical PASS from current validated PASS. State the exact next unfinished action when partial.
