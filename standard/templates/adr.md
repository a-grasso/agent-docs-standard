---
# File name: NNNN-slug.md  (e.g. 0007-event-schema.md): zero-padded, sequential
id: ADR-NNNN
title: <short imperative title, e.g. "Use append-only event schema">
status: proposed            # proposed | accepted | superseded | deprecated
date: <YYYY-MM-DD>
supersedes: <ADR-NNNN or ->   # optional
superseded-by: <ADR-NNNN or ->  # set when this ADR is later reversed
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

Do not point at the document that states this decision as current fact. That document cites
this ADR, never the reverse (§7.4.2.1): the citation belongs in the file that changes, so it
is repaired by the commit that invalidates it.
-->
