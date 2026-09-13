# Refactoring

Follow [Poteto Mode](../SKILL.md) for activation, authority, and delivery boundaries.

Identify the behavior to preserve and the structural problem to remove. Use existing coverage or a focused before/after check; add a characterization test when the changed behavior is otherwise unprotected and the test provides useful evidence.

Move in coherent steps. For internal API changes, find and migrate affected callers, including string-based references. Remove obsolete code once consumers have migrated; preserve compatibility when external consumers or staged rollout require it. Keep unrelated bug fixes or new behavior outside the refactor unless requested.

Explore architecture only when the target shape has consequential uncertainty. Delegate independent mechanical work when useful and permitted; crossing a function boundary does not require a design or delegation workflow.

Verify that the relevant behavior is preserved, run required checks, and complete the authorized delivery step. Report the structural improvement and evidence rather than requiring a particular number of commits or a PR for every refactor.
