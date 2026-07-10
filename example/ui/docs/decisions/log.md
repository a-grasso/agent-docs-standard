# Decision log (ui)

UI-scoped lightweight decisions. Newest first (standard §7.2.2).

---

## Signals for component state; no global store
**Date:** 2026-06-28 · **Tags:** [state, angular]

**Decision:** Use Angular signals and services for state; do not add NgRx or a global store.

**Why:** The dashboard's state is mostly server-derived and view-local; a global store added
ceremony without payoff in the spike. Revisit (promote to an ADR) only if cross-view shared
mutable state appears.

**Scope:** `ui` only.
