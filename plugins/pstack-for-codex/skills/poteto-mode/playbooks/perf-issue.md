# Performance issue

Follow [Poteto Mode](../SKILL.md) for activation, authority, and delivery boundaries.

Capture or reuse a representative baseline, name the metric, and locate the dominant cost. Inspect the relevant runtime path to ground the hypothesis. These strategy families are optional hypothesis generators:

   - **Elimination.** The cheapest work is work that doesn't run. Before optimizing the hot path, ask whether it needs to exist: a computation nobody consumes, a feature gate that's always off for this user, a sync that redundantly mirrors state, a legacy path kept "just in case". The trace shows what's slow, never that it's deletable, so confirm its consumers and purpose before deleting it. Deleting the work beats every other family when it applies.
   - **Divide and conquer.** The dominant cost scales with input size. Split the work so each piece touches less (chunk, shard, prune the search space) or so independent pieces run in parallel.
   - **Caching.** The same computation or fetch repeats on identical inputs. Store and reuse the result; name what invalidates it before claiming the win.
   - **Indirection.** The hot path does expensive work a cheaper intermediate could absorb: an index instead of a scan, a queue that shifts work off the interactive thread, a handle that lets a cheaper implementation swap in. Add the hop only when it removes more from the critical path than it adds; a layer that sits on the hot path without removing work is pure cost.
   - **Batching.** Many small operations each pay a fixed overhead (RPC, query, syscall, draw call). Coalesce them to pay the overhead once per batch.
   - **Redundancy.** The wait hangs on one slow instance or attempt. Duplicate the work (replicas, hedged requests, speculative execution) and take the fastest result. This trades extra load for lower tail latency, so the trace has to show the wait dominates and the system has headroom; duplication without that tradeoff only adds load.
   - **Lazy evaluation.** Cost lands on results that are never used or not needed yet (eager init on the boot path, rendering offscreen items). Defer the work until first use.
   - **Scheduling.** The work must happen, but not during the interactive moment. Move it to where nobody is waiting: idle callbacks, a background warmup after boot, precompute before the user arrives, cleanup after the frame commits. Distinct from Lazy (later-when-needed): Scheduling often runs the work *earlier* than the hot moment, or in its shadow. The win is perceived latency, so measure the interactive path, not total work done.

Choose a change supported by the evidence. Consider architecture or independent implementation only when it resolves a real uncertainty; a function boundary alone does not require either.

Compare before and after on equivalent workloads, account for measurement noise, and check affected correctness constraints. Report inconclusive measurements honestly. Stop when the requested target is met and relevant checks pass; repeat only for unresolved evidence or a requested optimization budget.

For explicitly requested sustained metric optimization, consult [hillclimb](hillclimb.md). Complete only the authorized delivery step. Report baseline, result, delta, workload, and evidence paths.
