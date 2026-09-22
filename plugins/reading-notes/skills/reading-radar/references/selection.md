# Search and selection ledger

## Rubric

Use the user's scoring model. This workflow's inherited default is E/F/P on 0–10 scales and total `10 × (0.45 E + 0.25 F + 0.30 P)` on 0–100. Show components and evidence. Scores express reading priority, not performance, probability or citation counts.

- **Effectiveness:** direct usefulness for the stated problem, implementation detail and relevant evaluation. Write topic-specific criteria first. For memory: write/update, conflict, merge, forgetting/eviction, exit/revocation/deletion and derived residuals. Do not apply memory criteria to unrelated topics.
- **Freshness:** publication/substantive revision date, relevance to current LLM systems and requested window. Label older anchors; do not fabricate a new publication date from access time. Keep publication, update and retrieval dates distinct.
- **Popularity:** for this user's rubric, company provenance and technical adoption/engineering ecosystem are proxies, not verified citation counts. Apply requested US/China/company preferences; do not substitute venue prestige or raw search rank.

Wrong identity, unsupported source or failure of a required review gate makes an item provisional/excluded regardless of score. If fewer than N qualify, report the shortfall or search within scope; never pad with invalid entries.

## Records to retain

Keep a machine-readable ledger in the work directory. Suggested JSON fields:

- `schema_version`, `topic`, `question`, `effectiveness_criteria`, `date_window`, `source_preferences`.
- `requested_stage`, `candidate_target`, `reading_target`, `scope_version`, `scope_changes` with prior/new values and user-request reference.
- `weights`, `score_scale`, `tie_break`, `review_policy` with reviewer count and unanimity/other explicit rule. Default ties preserve stable prior order; declare any secondary policy before selection.
- `search_runs`: lane, actual query, tool/provider, date, returned source IDs. Mark unavailable logs as unavailable; do not invent queries retrospectively.
- `sources`: stable `source_id`, canonical URL/DOI, title, organization/authors, type, dates, access level, snapshot path, related IDs, duplicate group, tags, scores/reasons and mechanism summary.
- `reviews`: source ID, reviewer identity, independent lane/run, validity, helpful yes/no/uncertain, E/F/P, reason and anchors. Preserve disagreements and missing votes. Model diversity does not prove correctness.
- `selection`: ordered source IDs/ranks, score snapshot, inclusion/exclusion reason, provisional/confirmed status, confirmation reference, frozen version. Confirmation may be explicit permission to produce this identified list.

Canonicalize arXiv versions/DOI/publisher aliases of one work. Link papers, implementations and engineering blogs as related; merge only when redundant for the learning goal. Keep distinct practical resources when they add different mechanisms, with a reason. Deduplicate across topics without erasing topic membership.

Three reviewers score independently before seeing other conclusions. If aggregation is needed, average E/F/P across complete reviews, then apply weights. Do not average a missing reviewer as zero or drop the missing reviewer. Preserve user-approved scores in production; proposed changes return to selection review.

Topic quotas change selection compared with global score order. Use only when explicitly requested/confirmed; record quota and final score order. No hard-coded six-topic portfolio allocation.

## Before production

Check identity/accessibility; recompute scores; confirm all required votes; freeze IDs, ranks, titles, URLs and output-bundle mapping. Return the shortlist and summaries here if that is all requested. Searching is not permission to overwrite a note or publish a site.
