# Loop

| Setting | Default |
|---------|---------|
| Max loops | 4 |

"max N loops" → max_loops = N.

1. Run the [Workflow](../SKILL.md#workflow) through validation. From loop 2 on, the change holds this session's own fixes: dispatch a reviewer subagent to run it on the same scope instead. The reviewer must:
   - Be a **separate subagent** (fresh context, no anchoring to your reasoning)
   - Receive only the **work product** (files, diffs) — not your thought process

   The reviewer subagent has no memory of prior loops — include prior feedback context explicitly in each reviewer prompt to avoid repeating resolved issues. Give it the original requirements too. Confirm each finding it returns against the code it quotes before you fix it.
2. Report to the user:
   ```
   Loop {N}/{max}:
   - {summary of key feedback points}
   ```
3. If the loop ended with no validated **Must fix** or **Should fix** finding → **stop, go to the report**
4. Revise: fix the validated **Must fix** and **Should fix** findings. **Nice to have** findings are optional. Each revision should be targeted. Don't rewrite everything — fix what the reviewer flagged. Maintain a list of ALL prior feedback to avoid regressions. Then run the checks those fixes need.
5. If loops completed >= max_loops → **stop, go to the report**. Otherwise go back to step 1.

max_loops limits the full review passes, not the fixes: the findings of the last pass are fixed too.

If a fix cannot be completed safely, leave that finding unfixed and name the concrete blocker in the report.

If the same finding survives 2 consecutive loops, stop and ask the user.

**Never** continue past max_loops without user consent.

## Final report

After the [Report](../SKILL.md#report) of the last pass, add:

- `Fixed:` the findings fixed, by loop.
- `Not fixed:` each finding left unfixed, with its concrete blocker.
- `Verification:` for the fixes of the last pass, which checks ran and their result, and whether those fixes were reviewed again. Fixes made after the last review pass have not been reviewed: say so, and never present them as reviewed.

Skip an empty `Fixed:` or `Not fixed:` line.
