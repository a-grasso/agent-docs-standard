---
# File name: YYYY-MM-DD-slug.md  (e.g. 2026-09-09-collector-0.155-to-0.156.md)
# The date is the filename's job (§7.2.3): the class sorts chronologically and every
# document in it is dated by construction.
title: <what happened, e.g. "Collector upgrade 0.155 to 0.156">
---

# <YYYY-MM-DD>: <what happened>

<One paragraph: the event, and why the project cared about it.>

## What happened
<The sequence, with times where they matter. Past tense is correct here: this document is
dated, so its reader can date every claim in it. §4.7 does not apply to a record (§7.1.3).>

## What was affected
<Scope and blast radius. Be specific about what was *not* affected too.>

## What changed as a result
<Code, config, or procedure changes this event caused. Link the ADR if it caused a decision;
a record states what happened, an ADR states what was chosen.>

<!--
A record is for an *event*, not a choice: an upgrade and its API drift, an incident and its
cause, a completed migration, a benchmark run, a dated audit. An event has no alternatives;
a decision does. Once written a record is never edited: a correction is a new record.

It is also not a plan or a status report. Work in flight belongs to the tracker (§7.3).
-->
