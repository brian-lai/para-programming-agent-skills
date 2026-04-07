# Phased Plans Feature: Changelog

**Date:** 2026-04-07
**Status:** Complete

---

## Summary

Phased plan support is available from v0.1.0. Complex work that spans multiple architectural layers or affects many files can be broken into independently reviewable and mergeable phases.

---

## Skills with Phased Plan Support

- **`/para-plan`** — Detects when work should be phased, creates master plan + sub-plans
- **`/para-execute --phase=N`** — Creates phase-specific worktrees and branches
- **`/para-summarize --phase=N`** — Creates phase-specific summaries, marks phase completed
- **`/para-archive`** — Cleans up all phase worktrees

## Common Phasing Patterns

1. **Layer-Based** (Database → API → Frontend)
2. **Strangler Pattern** (Add new → Migrate → Remove old)
3. **Zero-Downtime Migration** (Dual-write → Backfill → Switch → Cleanup)
4. **Infrastructure + Feature** (Setup → Core → Integration)
5. **Service Decomposition** (Extract → Deploy → Update clients → Remove)

## Documentation

- [Quick Reference Guide](./phased-plans-quick-reference.md)
- [Complete Example](./phased-plan-example.md)
