# CABUS hosted tracker: proposed design

Status: ready for review; implementation has not started.

## Intent and decisions

Improve the 4-in-1 system and deliver a hosted browser version with accounts. The user selected the hosted option after discussing costs; use free services only. Preserve the desktop app and all original data files.

## Approaches

1. Improve Tkinter only: least migration work, but does not provide the selected hosted access.
2. Build locally first and defer hosting: simpler initial setup, but does not complete the selected option.
3. Add a hosted web application, retaining desktop source: selected approach. It gives desktop/mobile browser access and account separation. Legacy data is imported intentionally; the two applications do not synchronize automatically.

Builder's technical proposal: Cloudflare Workers with static assets and D1, deployed on the Free plan at a provided `workers.dev` address. Use plain HTML/CSS/JavaScript for the interface and a small JavaScript Worker API. Keep the web app in `web/`, separate from the Python files. No paid packages or services.

## Experience

- **Overview:** four useful summaries, upcoming and overdue tasks, goal progress, recent workouts, and the selected month's spending/budget. Each summary links to its tracker and has a clear add action.
- **Goals:** create/edit/delete goals, choose short/long term, set a target date, manage milestones and toggle completion. Show due today separately from overdue. Completion derives from milestones.
- **Tasks:** create/edit/delete tasks with category, priority, status and validated deadline. Search/filter by status and category; mark complete directly. Use stable unique IDs.
- **Fitness:** start a workout, add/edit/remove exercises, save the workout, and browse history. Validate positive whole-number sets/reps and finite nonnegative weights. A server-stored draft survives navigation and refresh. Completed summaries count saved exercises before clearing the draft.
- **Expenses:** create/edit/delete dated expenses, filter/search, set a monthly budget, and show totals by category. Store amounts as integer centavos, format as PHP, and calculate spending and remaining budget for the selected month only. Store reminders per account.
- **Account/data:** register, sign in/out, change password with current-password verification, export own data, and preview/import legacy JSON. Show loading, empty, validation, error and success states. New accounts start empty.

## Visual and interaction proposal

Retain CABUS branding with a quieter dark palette and purple primary actions. Use clear hierarchy, consistent spacing, readable body text, restrained borders and native semantic controls. Desktop uses side navigation; small screens use compact navigation without horizontal overflow. Show actual tracker content immediately, with no continuous logo animation.

Dialogs have labels, inline errors, Escape/cancel behavior, initial focus, focus containment and focus restoration. All actions work with a keyboard and have visible focus. Respect reduced motion; use text labels alongside status colors and chart values. Synthetic records may appear only in an explicitly labeled development/demo mode; a new real account is empty.

## Identity and safety

Create new web accounts; do not silently import MySQL accounts or plain-text passwords. Normalize email addresses. Hash passwords with a unique random salt using a Worker-supported password derivation function; validate its work factor and free CPU-budget compatibility before committing to implementation. Reject the design's hosted release if a secure password scheme cannot run within the target rather than reducing password protection to fit.

Use opaque random sessions; store only token hashes in D1. Send host-only HttpOnly, Secure, SameSite cookies over hosted HTTPS; permit development-only localhost cookies. Rotate sessions on login, revoke on logout/password change, and expire sessions after a defined lifetime (proposal: seven days). Enforce same-origin checks on mutations, parameterized queries, ownership checks on every record operation, request-size limits and authentication throttling. Return generic login failures.

No unauthenticated email-only password reset. Initial recovery uses a one-time recovery code generated on account creation and shown once, stored as a hash; rotation invalidates the old code and all sessions. No outbound email or paid identity dependency. Recovery and login receive the same abuse protections.

## Data model and persistence

Use users, sessions, goals, milestones, tasks, workouts, exercises, monthly budgets, expenses, reminders and import receipts. Every tracker record has an owner ID. Index owner and date/status where queried. IDs are server-generated UUIDs. Date-only fields use validated ISO dates; define user-visible reporting dates in Asia/Manila initially. Store timestamps in UTC.

Use D1 transactions/batches for multi-record operations, including workout completion and imports. Validate at the API boundary, reject non-finite/negative amounts and invalid dates, and distinguish failed writes from successful updates. Preserve existing records on failed operations.

Legacy import accepts only explicitly selected tracker JSON, not arbitrary server paths. Preview counts and validation errors before confirmation. Regenerate IDs, preserving every distinct record even when old IDs collide. Import into the signed-in account only, with schema/size limits and an import receipt/content digest to prevent accidental replay. Do not ship root JSON files as public assets or upload them during deployment. Support export of the authenticated user's records for backup.

## Desktop improvement scope

After the web flows work, fix the demonstrated shared model defects in the existing desktop app: stable expense/task IDs (repair collisions without dropping records), calendar-day goal calculations, correct workout completion count, finite numeric/date validation, and safe JSON persistence that reports failures and preserves malformed input. Correct monthly expense reporting. Retain existing desktop authentication and screen structure in this pass; MySQL account migration and a full Tkinter redesign are outside this first release. Explain that legacy desktop records remain shared until an explicit desktop account migration is undertaken; isolation is guaranteed for the new web app.

## Free hosting and deployment

Stay on Cloudflare Free; no billing upgrade, paid domain, R2 uploads, email delivery, AI service or scheduled paid work. Static assets are served directly; only API routes invoke the Worker. Cloudflare's free request/database limits apply, and limit errors must produce a useful retry message rather than corrupt records.

Build and verify locally first with Wrangler and local D1. Deployment requires the user's Cloudflare account authorization. Complete all independent implementation and review before that authorization step. Create one named D1 database, apply the reviewed initial migration, and deploy to a provided `workers.dev` URL when authorized and available. If access is unavailable, deliver the tested runnable source plus exact deployment steps; report explicitly that it is not hosted yet.

## Acceptance checks

1. Register/sign in/out/recover/change password work; stored values are not plain-text passwords/session tokens.
2. Two accounts cannot list, read, update, delete, import into, or export each other's records.
3. CRUD and refresh/restart persistence work for all four trackers; validation failures do not mutate data.
4. Due-today goals show zero days; completed workout totals are correct; drafts survive refresh; monthly spending excludes other months.
5. Legacy import preserves duplicate-ID records, previews errors, commits atomically, and refuses accidental replay. Export round-trips through documented web backup import.
6. Failed saves/imports leave original records and legacy files intact.
7. Inspect rendered layouts at desktop and narrow mobile sizes; exercise keyboard navigation, dialogs, forms, empty states and errors.
8. Run targeted regression tests for desktop fixes using temporary files; retain original tracker JSON unchanged.
9. Verify deployment status and live URL if deployed. Never report a preview or package as a live hosted application.

## Builder discretion

Choose file structure, minimal test tooling, exact spacing/icon details, API route names and schema column details. Prefer standard platform features; avoid framework/dependency work that does not help the four workflows. Implement explicit recovery, throttle and session semantics as described; use secure defaults without adding paid dependencies. Hosting and capacity are constrained by provider terms and account availability, not promised unlimited service.
