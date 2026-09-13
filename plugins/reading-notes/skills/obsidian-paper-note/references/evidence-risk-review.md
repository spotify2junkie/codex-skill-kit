# Evidence and risk-review lens

Use this reference for AI, agents, recommendation, marketplace, trust and safety, fraud, product understanding, and risk-control sources.

## Evidence ladder

For every major claim, classify it before writing:

| Category | What belongs here |
|---|---|
| 论文计算事实 | Equations, dataset counts, table values, architecture connections, stated runtime or deployment facts |
| 作者解释 | The authors' account of why the method works or why a pattern appears |
| 我的迁移推断 | A proposed use in the user's system that the source did not test |
| 尚未证明 | Causal business impact, unseen slices, calibration, online reliability, or missing denominators |
| Shortcut | A simpler rule, retrieval, graph, classifier, or human-workbench baseline that could solve the same need |

Do not collapse these categories into a smooth narrative.

## Risk-control translation

Map the paper to the relevant unit of decision: account, seller, buyer, product, order, payment, promotion, device, relation, cluster, conversation, or investigation case. Then identify:

- signals available at decision time;
- labels and their maturity delay;
- batch, nearline, or online serving path;
- output schema and the actor allowed to take action;
- recall, incremental recall, precision, false-positive rate, loss rate, review cost, appeal rate, latency, and SLA;
- bad-case feedback, replay, time split, monitoring, drift, and rollback.

For TikTok or a comparable marketplace, discuss the closest scenario only when supported: account integrity, promotion abuse, organized fraud, seller or buyer risk, product safety, counterfeit or IP risk, content moderation, low-quality traffic, sanctions, AML, or refund abuse. A recommendation A/B result does not prove a fraud-control gain.

## Career and résumé translation

Write three levels:

- `可以作为知识表达`: concepts the reader can explain in an interview.
- `做完实验后可以写`: design or evaluation claims that require an implemented, measured project.
- `现在不能写`: ownership, launch, scale, causal uplift, or business savings not supported by the user's own evidence.

Turn the paper into interview or project language without inventing personal experience.

## Common traps

- **Generative score:** `P(token | prompt, generated prefix)` is not automatically `P(real-world violation | case)`. For Yes/No scoring, evaluate both fixed label sequences under the same decision prefix, normalize within the candidate set, and calibrate on a held-out, preferably time-split set.
- **RL reasoning plus classifier:** prevent conclusion leakage. Let the reasoner emit evidence checks or structured fields; let an independently evaluated classifier produce the final score. Compare direct classification, SFT, RL generation, and RL-reasoner-plus-classifier under the same data and compute budget.
- **Explanation as evidence:** attention, rationale, and judge scores can organize review but do not create facts.
- **Training names:** rejection-sampling followed by supervised training is still SFT unless the source defines an online preference or policy objective. Do not rename it OPD.
- **Agent autonomy:** a tool call or self-reflection loop is not RSI by itself. Record tools, permissions, memory, stopping conditions, feedback source, and who approves consequential actions.
- **Graph propagation:** homophily can spread both signal and contamination. Require time-aware holdouts, seed-quality audits, degree and popularity baselines, and cluster-level human review.

## Smallest falsifiable experiment

Pre-register one comparison that can fail. Use the simplest credible baseline, one proposed method, a time-based holdout, explicit unit and denominator, slice metrics, calibration, latency, review capacity, and a rollback rule. When RL is proposed, include at least:

```text
M0: direct classifier
M1: SFT structured classifier
M2: SFT → RL → constrained Yes/No score
M3: RL structured evidence → calibrated binary verifier
```

Do not recommend rollout unless the method improves the target slice without violating false-positive, calibration, latency, and review-cost guardrails.
