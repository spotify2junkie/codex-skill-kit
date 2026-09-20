# Public sources

This skill is an engineering synthesis, not an implementation of any paper's full system. It does not depend on a private reading note. Research results below do not establish that arbitrary skill merges are safe.

- [OpenAI — Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills): evaluate observable skill behavior with repeatable tasks; format checks alone are insufficient.
- [ACES — Evaluating Skills, Not Just Agents](https://arxiv.org/abs/2608.20614v1): motivates paired evaluation with and without skills under comparable conditions. Applied here to baseline/candidate comparisons; no claim of measured lift without runs.
- [SkillOpt — Executive Strategy for Self-Evolving Agent Skills](https://arxiv.org/abs/2605.23904v2): motivates bounded edits and evaluation before accepting a candidate. This skill does not run its optimization algorithm.
- [SkillChain — Closing the Loop on Skill Evolution for Image-Based E-Commerce AI Assistants](https://arxiv.org/abs/2606.12984v2): separates routing changes from skill-body refinement. Its e-commerce domain results are not evidence for general-purpose merge quality.

Paper versions pinned above were checked on 2026-09-21. The reconciliation rules and permission-preservation workflow are local design decisions, not quotations or universal conclusions from these papers.
