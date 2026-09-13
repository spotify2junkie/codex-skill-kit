---
name: poteto-mode
description: "Resolve software changes with coupled design, diagnosis, or delivery decisions; also use when poteto-mode is requested."
---

# Poteto Mode

Deliver the requested software outcome with the smallest process that resolves its actual uncertainty. Repository instructions own worktrees, required checks, and release gates.

## Activation

Use Lite for the current phase when a task has coupled design, diagnosis, or delivery decisions. Routine edits do not need this workflow. Use Full when `$poteto-mode` is the first non-whitespace token; an existing trusted sticky receipt may extend it across the session. Without that receipt, Full applies to the current turn. `disable $poteto-mode` ends sticky Full behavior. Full permits deeper exploration when useful; it does not mandate it.

## Decisions and completion

- Establish the observable outcome. For defects, identify the failing boundary from a bounded reproduction or existing decisive evidence.
- Make a coherent fix that addresses the cause and preserves the requested experience. Explore competing designs when a consequential contract or tradeoff remains unresolved.
- Verify the changed behavior and run required repository checks. Use existing coverage; add tests when they expose a meaningful regression. Live checks address behavior that local tests or CI cannot establish and require the relevant authorization.
- Continue through fixes and the authorized delivery step. Reuse authorization already supplied. A working first draft is incomplete when requested validation or delivery remains.

## Read only the relevant procedure

Consult a playbook when its task-specific detail is needed; it is not a checklist to load before every edit.

- New behavior: [feature](playbooks/feature.md).
- Defect: [bug fix](playbooks/bug-fix.md).
- Measured slowness: [performance](playbooks/perf-issue.md).
- Behavior-preserving restructuring: [refactoring](playbooks/refactoring.md).
- Read-only investigation: [investigation](playbooks/investigation.md).
- Runtime or profiling evidence: [runtime forensics](playbooks/runtime-forensics.md) or [trace forensics](playbooks/trace-forensics.md).
- A throwaway decision aid: [prototype](playbooks/prototype.md).
- Resuming prior work: [session pickup](playbooks/session-pickup.md).
- An explicitly requested sustained autonomous workflow: [autonomous run](playbooks/autonomous-run.md).

For release, use the repository's release owner. Otherwise consult [opening a PR](playbooks/opening-a-pr.md), [PR status and repair](playbooks/babysit.md), or [shipping](playbooks/shipping.md) only for that authorized phase. Loading this skill does not authorize PR creation, messages, monitoring, deployment, or production changes.

## Supporting skills and delegation

Load another skill only for guidance this task needs. Do not automatically load principle, architecture, writing, or review bundles. Independent review and delegation are optional unless the user or repository requires them; use them when a bounded independent task adds evidence or saves time, subject to runtime permissions.

When delegating, read [runtime and isolation rules](references/codex-agent-runtime.md). Use the installed `pstack-poteto-agent` profile when available, otherwise the [delegate prompt](references/poteto-agent-prompt.md). The parent owns integration and checks the resulting artifact. Do not load delegate instructions without a delegation task.

Report the outcome, material decisions, relevant verification, and actual delivery status. State unresolved blockers precisely.
