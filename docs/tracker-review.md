# CABUS 4-in-1 tracker review

Reviewed: 2026-10-28. Scope: current Python/Tkinter application and the user's request to improve reliability, design, and add a web version. This is an assessment, not an approved implementation design.

## Confirmed findings

| Priority | Finding | Evidence and consequence |
| --- | --- | --- |
| High | Tracker records are shared between accounts | `main.py` creates all managers before authentication, with global JSON paths. Login passes a display name; no user ID scopes records. |
| High | Passwords are stored in plain text | `database.py` inserts passwords directly and compares them with equality. Reset updates the password without verifying ownership. |
| High | Expense IDs collide | `ExpenseManager.add_expense` uses list length. In an isolated reproduction, add three, delete ID 1, add another produces IDs `[2, 2, 0]`; deleting ID 2 removes two records. |
| High | Task IDs already collide in saved data | `tasks_data.json` contains two records with ID 2. The form uses list length plus one, while update/delete select by ID. A migration must preserve both records with distinct IDs. |
| High | Damaged data appears empty | JSON read failures reset lists. An isolated malformed expense file loaded as an empty list; a subsequent save could replace the damaged file. |
| High | Saves truncate files directly | Managers open the live JSON file with mode `w`, with no atomic replacement or recoverable backup. Some save errors only print to stdout. |
| Medium | Monthly budget uses all-time spending | Expense total and remaining-budget methods sum all records regardless of month. |
| Medium | Goals due today show minus one day | `get_days_remaining` subtracts the current time from midnight. Isolated reproduction returned -1 for today's date. |
| Medium | Workout completion reports zero exercises | The manager clears the workout before the page counts exercises in its success message. Isolated reproduction confirmed the post-save count is zero. |
| Medium | Numeric validation permits invalid values | Expense input accepts `NaN` because the positivity check does not reject it. Fitness accepts negative sets/reps/weights; task dates are not validated before saving. |
| Medium | Reminders are temporary | Expense reminders live on the Tk root rather than in persisted data. |
| Medium | Keyboard and scrolling behavior is fragile | Canvas buttons bind mouse clicks without keyboard activation. Tasks install a global mousewheel binding targeting a page canvas. |
| Medium | Overview does not summarize the trackers | Dashboard home repeatedly redraws an animated logo rather than displaying actionable records. Navigation and login use large fixed dimensions. |
| Setup | Startup depends on an external MySQL service | Previous launch required installing the connector. No listener was observed on local port 3306; successful authentication has not been verified. |

## Recommended direction

Preserve the desktop application and original JSON files. Build a local web app as an additive interface first, with a clear path to hosting after review. The user has requested desktop improvements, visual improvements, and a web version; the local-versus-hosted decision is pending.

1. Establish reliable local startup and storage; use stable IDs, explicit validation, safe writes and visible failure feedback.
2. Add real account boundaries and password hashing; remove unauthenticated password replacement. Do not automatically assign shared legacy data to every new user.
3. Repair the confirmed desktop defects, including monthly expense calculations, due dates, workout state and completion feedback.
4. Create a responsive web interface with Overview, Goals, Tasks, Fitness and Expenses. Show due tasks, goal progress, recent workouts and monthly budget together, with clear add actions.
5. Support a deliberate import of legacy JSON records into an account, with original files retained and duplicate IDs repaired. Keep desktop/web synchronization out of the initial scope unless explicitly selected.
6. Verify behavior using temporary data, account-isolation and persistence tests, then inspect desktop/mobile layouts and keyboard interactions.

## Proposed visual direction

Retain CABUS branding and the purple accent. Use a restrained dark interface, consistent typography and spacing, readable surfaces, visible focus, labeled controls and practical empty states. Put tracking information and quick actions above decoration. Charts should have readable labels and textual totals.

## Review limits

The reproductions used temporary files and did not alter the user's tracker records. No code changes, account migration, website deployment or full interactive UI verification were performed during this assessment.
