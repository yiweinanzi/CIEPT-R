# Persistent Agent Workflow

Every future agent session must follow this workflow.

## Session Rules

1. Read `continue/task.json` before making changes.
2. Select exactly one task whose `status` is `pending` and whose `depends_on` values are all `done`.
3. Use test-first execution for code changes whenever practical.
4. Do not mark a task `done` until verification has been run and recorded.
5. Update `continue/progress.md` in the same session.
6. Update `continue/task.json` in the same session.
7. Make one coherent commit for the completed task.

## Blocked Task Rule

If a task cannot be completed:

- set its `status` to `blocked`
- record the exact blocker in `continue/progress.md`
- do not commit a fake completion

## Progress Entry Format

Use this format in `continue/progress.md`:

```md
## YYYY-MM-DD HH:MM UTC - TASK_ID

- Goal:
- Changes:
- Verification:
- Risks/Next:
```
