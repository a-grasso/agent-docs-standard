---
# File name: NNNN-slug.md  (e.g. 0007-event-schema.md): zero-padded, sequential
id: ADR-NNNN
title: <short imperative title, e.g. "Use append-only event schema">
status: proposed            # proposed | accepted | superseded | deprecated
date: <YYYY-MM-DD>
supersedes: <ADR-NNNN or ->   # optional
superseded-by: <ADR-NNNN or ->  # set when this ADR is later reversed
decides: <tracker ref, e.g. acme/platform#412>   # the issue this closes (§7.3.5)
normative-in: <path to the doc that states this as current fact>
revisit-when: <a condition a reader can check>   # omitting this asserts permanence
---

# ADR-NNNN: <title>

## Context
<The forces at play: the problem, constraints, and what makes this decision non-obvious.
What is true about the world that requires a decision?>

## Decision
<The choice, stated in one or two sentences, in the active voice: "We will ...">

## Consequences
- **Positive:** <what this buys us>
- **Negative / cost:** <what it costs us, what becomes harder>
- **Follow-ups:** <work this decision creates, other ADRs it affects>

## Alternatives considered
- **<Option B>**: <why not>
- **<Option C>**: <why not>

<!--
`revisit-when` must be checkable. "When cost per signal type is measured" is checkable;
"when we have more data" is not, and degrades the field into "revisit later", which is the
same as no field. Leave it out entirely if the decision really is permanent: its absence is
a claim, and that is the point. A provisional decision and a settled one look identical the
moment they are written, and an accepted ADR is immutable, so nothing else tells them apart.

`normative-in` names the one mutable document allowed to state this decision as current
fact (§7.4.2). The ADR holds the rationale; that document holds the answer and links back.
-->
