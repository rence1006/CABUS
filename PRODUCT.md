# CABUS

<!-- impeccable:product-schema 1 -->

## Platform

web

The existing Python/Tkinter desktop application remains available alongside the new web application.

## Stack

Existing desktop: Python, Tkinter, MySQL authentication, JSON tracker storage.

Proposed web stack, pending design approval: plain HTML/CSS/JavaScript, a Cloudflare Worker API, and D1 database. Cloudflare Free plan is the deployment target.

## Product Purpose

Bring goals, tasks, fitness, and expenses into one tracker. The user requested improvements to the existing system, better design and usability, and a hosted version with accounts and access from other devices.

## Operating Context

The current application runs on Windows. The user selected hosted web access and accepted a free-hosting-only direction. Existing personal tracker files are in the project root.

## Capabilities and Constraints

- Four trackers: Goals, Tasks, Fitness, Expenses.
- Accounts and separate records for each user.
- Browser access on desktop and mobile.
- No paid hosting, purchased domain, paid add-ons, or automatic plan upgrades.
- Preserve original tracker files. Ownership of the existing shared data is not established; import must be deliberate.
- Web and desktop synchronization is an open future decision; initial proposal is an additive web app.

## Brand Commitments

Existing product name: CABUS. Existing visual identity uses dark backgrounds and a purple accent. Retaining these is the proposed starting point, rather than a user-mandated aesthetic.

## Evidence on Hand

`docs/tracker-review.md` records the code audit and isolated bug reproductions. Existing JSON records demonstrate the current schemas. They are private data, not website assets or demo content.

## Open Decisions

- Approval of the proposed implementation design.
- Cloudflare account access for final deployment.
- Whether public registration should remain available after the owner's initial account is created; proposal: explicit account creation, with per-account isolation and rate limits.
