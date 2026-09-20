# Reconciliation decisions

| Observed relationship | Preferred change | Evidence to check |
| --- | --- | --- |
| Same trigger, purpose, outputs and constraints | Consolidate into one owner | Exceptions, dependencies and callers survive |
| Shared mechanics but different outputs or domains | Extract shared script/reference; retain entrypoints | Shared abstraction does not erase domain rules |
| Complementary stages, such as discovery then summarization | Keep stages and define the handoff | Input/output shape and who writes the final artifact |
| Descriptions overlap but bodies do different work | Narrow discovery descriptions | Positive and near-match negative requests |
| Same condition requires incompatible outcomes | Resolve authority and intent, or ask a concrete missing choice | Neither a union nor an intersection silently preserves both |
| Different conditions appear contradictory | Express the conditions as separate modes | Each mode retains its own success cases |
| Upstream release plus local customizations | Compare old upstream, local, new upstream | Preserve intentional local behavior; identify incompatible changes |
| Same skill installed from multiple sources | Identify active source and differences before deduplication | Installed paths, discovery metadata, package ownership |

Example: one reading skill writes one combined note for a batch, while another writes one note per source. Preserve both as explicit modes if that matches the user's intent; do not silently create extra notes. A summary stage may hand structured content to a note-writing stage without owning a second output file.

Rule map example:

| Original rule | Condition | Disposition | Destination | Reason |
| --- | --- | --- | --- | --- |
| A: one note per batch | Default batch request | Keep | Combined mode | Existing output contract |
| B: one note per source | User explicitly requests separate notes | Specialize | Separate mode | Preserve supported alternate output |
| B: write to a personal absolute path | No destination provided | Replace only if portability is requested | Destination resolution | Private path is not portable; preserve explicit configured destinations |

If B instead requires separate notes unconditionally and the request gives no precedence, that conflict needs a decision rather than this assumed specialization.

Keep evidence proportionate: for one duplicated sentence, a brief explanation can replace a full table. For public delivery, exclude credentials, private examples, and personal paths from patches and test artifacts.
