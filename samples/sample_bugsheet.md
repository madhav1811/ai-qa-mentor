# Bug Sheet — TaskFlow — Tester: Alice — 2026-08-10

## Tested
- Signed up with a valid email/password (>=8 chars) — works.
- Logged in with correct credentials — works.
- Created a task with title only — works.
- Created a task with title + due date + priority — works.
- Marked a task complete, then reopened it — works.
- Deleted a task, confirmed it appears in Trash — works.
- Assigned a task to a teammate, teammate got the notification email — works.

## Bugs found
- BUG-101: Password reset link does not actually expire after 1 hour — tested at 90 minutes, link still worked.
- BUG-102: Removing a team member did not revoke their access immediately; they could still open team tasks for a few minutes.
