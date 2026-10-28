# CABUS — 4-in-1 tracker

Goals, tasks, fitness, and expenses in one workspace.

[Open the hosted app](https://cabus-tracker.repulse-coach-worker.workers.dev/)

## Web app

Private accounts, persistent workout drafts, monthly budgets, reminders, and JSON import/export. Each account has separate data, with protection against conflicting saves and account switches in other tabs.

Requires Node.js 24 or newer:

```powershell
cd web
node server.mjs
```

Open http://127.0.0.1:4174 and create an account. Save your recovery code. See [web setup and deployment](web/README.md) for Cloudflare Workers Free and D1 instructions. The committed database ID is a placeholder; use your own D1 database for a new deployment.

## Desktop app

The original Python/Tkinter application is included with persistence and tracking fixes. It still requires MySQL for authentication.

```powershell
python -m pip install mysql-connector-python
$env:CABUS_DB_PASSWORD = 'your-local-mysql-password'
python main.py
```

Optional environment variables: `CABUS_DB_HOST`, `CABUS_DB_USER`, `CABUS_DB_NAME`. Personal JSON files are created locally and excluded from Git. The desktop app and web app do not automatically synchronize.

## Checks

```powershell
node --test "web/tests/*.test.mjs"
python -m unittest discover -s tests -v
```

The separate `preview/` directory is the original interactive sample-data mockup. Account and cloud-storage features live in `web/`.

No personal tracker records, local databases, credentials, or installed dependencies are included in this repository. Existing desktop authentication remains a legacy component; use the web app for per-account tracker isolation.
