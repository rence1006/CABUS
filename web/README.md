# CABUS web tracker

The approved interface now uses a server API, private accounts and durable storage. New accounts start empty; original desktop records are never served as website assets. The original `preview/` remains a separate sample-data demo.

## Run locally

Requires Node.js 24+. No packages are required for the local app or unit tests.

```
cd web
node server.mjs
```

Open http://127.0.0.1:4174. Register a new account with a password of 12–128 characters. Save the recovery code shown once after registration. It replaces an email-based password reset: without your password or recovery code there is no automatic account recovery.

The local database is `web/.local/cabus.sqlite`, separate from root legacy JSON. Stop the server before copying the SQLite database for backup, or use the signed-in account's JSON export. `PORT` and `CABUS_DB_PATH` optionally override local settings. The server binds only to loopback; the development cookie exception does not apply on hosted HTTPS.

```
node --test tests/*.test.mjs
```

## Storage and conflict handling

Each account owns one validated tracker document in D1. A single compare-and-swap update writes the entire document atomically and increments its version. A stale tab receives HTTP 409 without overwriting newer records. Records have stable IDs; clients cannot choose another user's owner ID. Import/export use the same owner-scoped document and schema. Request limit: 512 KiB; individual tracker limit: 2,000 records; exercise/milestone limit: 200. This is designed for personal use; move to paginated relational records if those limits become constraining.

Data writes also require `X-CABUS-Account` to match the authenticated account ID captured when the browser loaded its data. Reads check this header when supplied. A shared-cookie account switch in another tab returns HTTP 409 with `code: account_changed`, rather than saving an old account's snapshot into the newly signed-in account. This header is a consistency guard, never an ownership selector.

## Authentication

New passwords use scrypt (N=16384, r=8, p=5; OWASP 16 MiB profile) with a unique random 256-bit salt. Local PBKDF2 account hashes remain readable. Cloudflare rejected the previous PBKDF2 work factor; it was not reduced. Random sessions and recovery codes are stored only as SHA-256 hashes. Sessions expire after seven days, rotate on login, and are invalidated together after password change/recovery through an authentication epoch. Hosted cookies are HttpOnly, Secure, SameSite=Strict and host-only. Mutation requests require the matching Origin. Login/recovery/change-password attempts are limited to five per 15 minutes per source and account; registration has an independent limit. This limit is intentionally strict for a personal tracker and may affect several people sharing a network.

The Worker uses the native `node:crypto` implementation, supported by Cloudflare at the configured compatibility date. Do not lower the password derivation work factor to meet a hosting limit. Local execution verifies functionality, not Cloudflare production CPU accounting. **Before hosted release, verify registration/login against an actual Free-plan Worker. If it exceeds the Free plan's CPU budget, keep the app local until a secure free identity solution is selected; never silently upgrade billing or weaken hashing.**

Official references: [Workers crypto](https://developers.cloudflare.com/workers/runtime-apis/nodejs/crypto/), [Workers Free limits](https://developers.cloudflare.com/workers/platform/limits/), [D1 pricing](https://developers.cloudflare.com/d1/platform/pricing/).

## Deploy on Cloudflare Free

Cloudflare account authorization is required. No paid plan, domain purchase, email provider, or paid storage is required by this app. Free usage limits still apply. An app running locally is not a hosted deployment.

1. Install the pinned development tooling with `npm ci` (first setup uses `npm install`).
2. Run `npx wrangler login` and complete Cloudflare authorization in your browser. Stay on Workers Free.
3. Run `npx wrangler d1 create cabus-tracker`. Replace the all-zero `database_id` in `wrangler.jsonc` with the returned database ID; do not put API tokens in the source tree.
4. Review `migrations/0001.sql`, then run `npx wrangler d1 migrations apply cabus-tracker --remote`. This creates the app tables only.
5. Run `npx wrangler deploy --dry-run`, then `npx wrangler deploy`.
6. Open the returned HTTPS `workers.dev` URL. Verify registration/login CPU usage on the Free plan, recovery, a tracker write/reload, and account isolation before adding private real data. The 512 KiB body limit bounds per-account document size. Monitor free request/database capacity in the provider dashboard.

Only `web/public/` is uploaded as static assets, alongside Worker source. Do not copy desktop JSON, `.local`, secrets, database files or test outputs into that folder. Production intentionally has no `DEVELOPMENT` variable. On Cloudflare database/limit errors the API returns a retryable error; it does not replace existing records with empty data.

