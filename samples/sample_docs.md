# TaskFlow — Product Documentation (excerpt)

TaskFlow is a task management web app.

## Authentication
- Users can sign up with an email and password. Password must be at least 8 characters.
- Users can log in with email + password.
- If login fails 5 times in a row, the account is locked for 15 minutes.
- Users can reset their password via an emailed reset link that expires after 1 hour.

## Task management
- Users can create a task with a title (required) and optional description, due date, and priority (low/medium/high).
- Users can mark a task as complete or reopen a completed task.
- Users can delete a task. Deleted tasks go to a "Trash" view and are permanently removed after 30 days.
- Tasks can be assigned to another user on the same team; the assignee gets a notification.
- Overdue tasks (past due date, not completed) are highlighted in red on the dashboard.

## Teams
- A user can create a team and invite others by email.
- Team admins can remove members; removed members lose access to team tasks immediately.
- A team must always have at least one admin — the last admin cannot leave or be removed.

## Notifications
- Users receive an email notification when assigned a task.
- Users receive an email notification 24 hours before a task's due date, if not yet completed.
