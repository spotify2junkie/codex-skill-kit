# Bug fix

The parent owns diagnosis, integration and verification. Follow the main
SKILL.md for activation, progressive loading, authority and release ownership.

1. Reproduce the reported behavior with one bounded check on the matching
   surface. Use an isolated fixture when a production mutation is outside scope.
   Distinguish environment failures from the defect.
2. Trace the failing boundary and choose the smallest coherent fix. Use existing
   evidence instead of repeating expensive live measurements. Consider deeper
   design only when materially different designs remain and affect contracts,
   persistence, concurrency, security or rollback.
3. Implement in the repository-required primary worktree. Follow the user's
   delegation choice and repository/runtime isolation rules; independent work
   is useful only when it changes the decision or reduces elapsed time.
4. Verify that the original reproduction now passes, then run the affected
   regression and required static/build gates. Add a cheap meaningful regression
   for the failing behavior; follow the repository's commit conventions.
5. Hand review/PR/release to the repository's release owner when available.
   Existing authorization persists; finish the reviewable implementation before
   asking for genuinely missing release authority.

An unavailable supporting skill is not a reason to stop an otherwise executable
fix. Ordinary function boundaries do not mandate architecture agents, mandatory
fan-out or additional workflow owners. No heartbeat or new user-owned task is
created without the user's request for that lifecycle.

Report the defect, root cause, change, red/green evidence and actual delivery
status. Never label a wrong-surface or inconclusive check as a pass.
