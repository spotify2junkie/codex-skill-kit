# Framework data flow

Framework data flow lets a reader trace each important module from a real input object to the next consumer.

## Sub-features

- `framework-provenance` distinguishes a source figure from a teaching redraw.
- `framework-input` names the data, tensor, graph, prompt, or event that enters a module.
- `framework-operation-output` states the actual computation and resulting object.
- `framework-downstream` names the next module or decision that consumes the output.

## How to get to it (user POV)

- Open `架构图与数据流` in the Markdown note.
- Open the framework figure.
- Go to page 7 of the embedded PDF.
- Read the row for each major stage from input through downstream.

## Driving it with ONV CLI

Preconditions:

- The note contains a resolvable framework image.
- The PDF uses the strict 10-page layout.

- **Verify the note.** Require `note.framework_io` and `note.figure_provenance` to pass.
- **Verify page 7.** Require `pdf.framework_io` to find figure provenance plus `输入`, `操作`, `输出`, and `下游` on the framework page.
- **Check semantics.** Compare page 7 with the Markdown explanation. Confirm module names are not substitutes for data objects or computations.
- **Proof.** Inspect page 7 in the contact sheet at readable zoom and include the visual attestation in the run.

## Gotchas

- `Attention`, `Capsule`, `Agent`, or `Graph-Aware` is a name, not an operation description.
- An attention weight is a model signal, not a causal label.
- If the source has no framework, a labeled teaching redraw is acceptable; an unlabeled invented figure is not.
- A module without a named downstream leaves the system boundary ambiguous.
