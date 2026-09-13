# ONV verification contract

Use this reference when a check fails, when adapting ONV to a new note collection, or when deciding whether a variation still satisfies the user's reading standard.

## Reader contract

The note has two reading speeds:

- Markdown is the auditable engineering record. It keeps the conclusion, insight, source framework, training objective, evidence boundary, and migration experiment. It does not need to repeat every comic card.
- The embedded PDF is the first-pass teaching layer. It uses Explain Like I Am Five without turning paper claims into cartoons presented as facts.

The note and PDF must agree about the model's inputs, operations, outputs, metrics, and limitations.

## Markdown requirements

A passing article section contains:

- article/source information and one embedded PDF;
- one sentence conclusion and a main flow;
- why the article matters to the reader's risk-control work;
- a framework figure with clear provenance;
- an explicit `input -> operation -> output -> downstream` explanation;
- training, Loss, Reward, Objective, or an explicit statement that the source discloses no training objective;
- evidence and boundary, migration, fact-checking, insight, and shortcut analysis;
- a production boundary in which model output is evidence or a score, while rules or human review own consequential action.

An original paper figure is preferred. If the source has no verifiable figure, a teaching redraw is allowed only when the note and PDF label it `教学重绘` or `原文未提供可核验架构图`.

## ELI5 PDF requirements

The strict 10-page template is:

1. conclusion, main flow, fixed roles, and color legend;
2. to 6. ten dependency-ordered concept cards, two cards per page;
7. source framework or explicitly labeled teaching redraw, plus input/operation/output/downstream;
8. training and Loss/Reward/Objective ledger, including what updates and what is not disclosed;
9. metrics, evidence layers, business denominators, and critical boundaries;
10. a smallest falsifiable migration experiment and a three- or four-stop learning route.

Each concept card has one `烦恼` panel and one `办法` panel. Beneath it are exactly two lines: `解决了什么` and `代价是什么`. The PDF should contain 8 to 13 concepts in general; the strict current template contains exactly 10.

Teaching values must be labeled `示意值`. Paper values retain their source, sample size, denominator, and author-reported status. Simplification cannot remove a consequential limitation.

## Framework and data flow

For every major module, the reader must be able to answer:

```text
input data or tensor
-> operation, rule, model, or aggregation
-> output data or tensor
-> downstream consumer or decision
```

Module names are not explanations. The note must distinguish what the structure computes, what training asks it to learn, and whether experiments prove that interpretation.

## Critical-thinking requirements

ONV expects all of these layers:

- calculation facts that can be checked in the source;
- the author's interpretation or deployment claim;
- what remains undisclosed or unproved;
- at least one plausible shortcut or simpler internal solution;
- the smallest experiment that could fail the migration hypothesis.

The note must not equate an attention score with causal evidence, a benchmark gain with business impact, deployment with a causal loss reduction, or a generated candidate with an enforcement fact. It must separate technical metrics, localization evidence when relevant, and business metrics such as loss, false positives, appeals, review cost, latency, and SLA.

## Pass semantics

`AUTOMATED_PASS` means the files, structure, counts, page layout contract, and rendered evidence were produced successfully. It does not prove visual quality.

`ONV_PASS` requires `AUTOMATED_PASS` plus a visual reviewer who inspected the latest contact sheet and recorded a pass. If the source hashes change, the run is stale and must not be reused.
