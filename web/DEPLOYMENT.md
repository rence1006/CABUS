# CABUS deployment

Live URL: https://cabus-tracker.repulse-coach-worker.workers.dev

Verified on 2026-10-28. Version: `57dae18a-ed97-47b4-9dec-a8d5f0229e6c`.

The user confirmed Workers Free. No billing upgrade or custom domain purchase was performed. D1 database `cabus-tracker` is deployed in APAC. Root personal JSON files were not uploaded.

Live checks passed: account registration, sign-in, data write/read, stale-version conflict, account isolation including account-switched tab writes, and logout. The two synthetic accounts created for this check were subsequently removed by exact IDs. There is no preset test login; create an account and save its one-time recovery code.

The previous PBKDF2 implementation failed on the hosted runtime's 100,000-iteration cap. New passwords now use scrypt with the OWASP 16 MiB profile (N=16384, r=8, p=5) and a unique 256-bit salt. Local preexisting PBKDF2 hashes remain readable. The secure work factor was not lowered. All 20 web regression tests pass after this change; 22 desktop regression tests passed in the completed desktop work.

Successful hosted smoke checks prove these tested flows execute on the current plan. They do not promise unlimited capacity; provider usage limits continue to apply.
