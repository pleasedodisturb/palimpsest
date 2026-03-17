# Skill: Auto-Commit (Git Checkpoint)

Creates a quick git checkpoint with a timestamped commit message. Use this at regular intervals during a session to preserve work.

## When to Use

- Every 15-20 minutes of active work
- After completing a logical unit of work
- Before switching context or starting something risky

## Steps

1. Verify the current directory is a git repository
2. Stage all changes: `git add -A`
3. Commit with a timestamped message:
   ```
   wip: checkpoint [YYYY-MM-DD HH:MM]
   ```
4. Do NOT push — this is a local checkpoint only

## Rules

- If there are no changes to stage, do nothing and report "No changes to commit"
- If the directory is not a git repo, stop and report the error
- Never force-add files that are in `.gitignore`
- Use `wip` type for checkpoints. Use a more specific type (`docs`, `feat`, `fix`) if the changes have a clear purpose
