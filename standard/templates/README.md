# Templates

Copy-ready files for adopting the Agent Docs Standard. See [`../SPEC.md`](../SPEC.md) for the
rules each template implements.

| Template | Use for | Spec |
|----------|---------|------|
| [`AGENTS.project-index.md`](./AGENTS.project-index.md) | the repository root context file | §3-§6 |
| [`AGENTS.module.md`](./AGENTS.module.md) | each module's context file | §3-§5 |
| [`adr.md`](./adr.md) | an Architecture Decision Record (`docs/adr/NNNN-slug.md`) | §7.2.1 |
| [`decision.md`](./decision.md) | a lightweight decision (`docs/decisions/`) | §7.2.2 |
| [`record.md`](./record.md) | a dated record of an event (`docs/records/YYYY-MM-DD-slug.md`) | §7.2.3 |

## The context-file templates are prompts, not forms

§4.5.3 forbids the uniform outcome, not the tool. A template may start you off, but every
heading you have nothing admissible to say under must be **deleted** rather than padded
(§4.5.1). Two sibling modules with identical section sets are evidence that headings were
filled rather than nodes described, which is how derivable filler enters a project at scale.
The comment block at the top of each template says this too; delete it once the file is real.

## Adopting in 5 minutes

1. Copy `AGENTS.project-index.md` to your repo root as `AGENTS.md`; fill it in, and delete
   what does not apply.
2. Alias it: `ln -s AGENTS.md CLAUDE.md`.
3. For each module, copy `AGENTS.module.md` to `<module>/AGENTS.md`, set `up:` to the root, and
   symlink `CLAUDE.md` beside it. Add each module to the root's `ref:`.
4. Declare cross-repo and external dependencies as `dep:` entries.
5. Start capturing decisions in `docs/adr/`. Keep work in flight in your issue tracker, not in
   `docs/`: docs describe, issues track (§7.3).

That gets you to Level 2 conformance (§9). Level 3 follows as you use `docs/`.

## Scaffolding

A `README.md` and any `_`-prefixed file inside `docs/` is scaffolding, not a record: class
naming and lifecycle rules do not apply to it (§7.1.4). So a class template is best kept in
the class it serves, e.g. `docs/records/_template.md`, where the author writing a record will
actually meet it.
