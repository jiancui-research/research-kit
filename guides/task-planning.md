# Derive and maintain the work queue

Loaded by `/research.plan` after the study design is settled. Write
`./.research/tasks.md` from `./.research/templates/tasks-template.md`.
Keep architecture and methodology in `plan.md`; keep executable work in `tasks.md`.

1. Read the current `plan.md`, proposal contribution IDs, and existing `tasks.md`
   and `claims.md` when present. Do not mark work complete just because code exists.
2. Build these queue sections:
   - **Setup:** environment, data access, and manuscript setup. Manuscript setup is
     `[USER-LED]` and can wait until an explicitly selected Paper task needs it.
   - **Build:** components in the plan's declared code directory. Match the paper
     type: a measurement or SoK paper may need little implementation.
   - **Eval:** one task per evaluation, decisive test first. Each names a claim ID,
     dataset, baselines, metric, falsifier, and any Build dependencies.
   - **Paper `[USER-LED]`:** one task per section, READY or BLOCKED on named evidence.
     Use the paper-type skeleton. Default implementation must skip these tasks.
   - **Polish:** reproduction pass, figures, tables, and documentation as needed.
3. Give every task a stable T-ID, a done-when criterion, and explicit dependencies.
   Use `[P]` for work that can run independently. Every evidence-blocked Paper task
   must link to a claim ID and the Eval task that will address it.
4. On re-runs, preserve checkbox states, IDs, done-notes, and dependency history.
   Add or refine work to match the changed plan. Mark obsolete work superseded
   with a reason instead of silently deleting its history or recycling its ID.
   If a completed task's evidence became stale, explain it and add a follow-up.
5. For legacy `tasks/design.md`, `tasks/eval.md`, and `tasks/paper.md`, carry their
   task IDs, checkbox states, and notes into the unified queue when requested.
   Keep the original files. Treat `[HUMAN]` as `[USER-LED]` during migration.

Validate the queue against the plan: no missing dependencies, no invented done
states, no manuscript work eligible for default execution. Report task counts and
the changes made. `/research.implement` executes the resulting queue.
