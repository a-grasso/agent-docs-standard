# Templates

Copy-ready files for adopting the Agent Docs Standard. See [`../SPEC.md`](../SPEC.md) for the
rules each template implements.

| Template | Use for | Spec |
|----------|---------|------|
| [`AGENTS.project-index.md`](./AGENTS.project-index.md) | the repository root context file | §3–§6 |
| [`AGENTS.module.md`](./AGENTS.module.md) | each module's context file | §3–§5 |
| [`adr.md`](./adr.md) | an Architecture Decision Record (`docs/adr/NNNN-slug.md`) | §7.2.1 |
| [`decision.md`](./decision.md) | a lightweight decision (`docs/decisions/`) | §7.2.2 |
| [`plan.md`](./plan.md) | an ephemeral feature plan (`docs/plans/`) | §7.3.1 |
| [`review.md`](./review.md) | an ephemeral feature review (`docs/reviews/`) | §7.3.2 |

## Adopting in 5 minutes

1. Copy `AGENTS.project-index.md` to your repo root as `AGENTS.md`; fill in the placeholders.
2. Alias it: `ln -s AGENTS.md CLAUDE.md`.
3. For each module, copy `AGENTS.module.md` to `<module>/AGENTS.md`, set `up:` to the root, and
   symlink `CLAUDE.md` beside it. Add each module to the root's `ref:`.
4. Declare cross-repo / external dependencies as `dep:` entries.
5. Start capturing decisions in `docs/adr/`; keep feature work in `docs/plans/` and
   `docs/reviews/`, and garbage-collect it when features land.

You are now Level 2 conformant (§9). Level 3 follows naturally as you use `docs/`.
