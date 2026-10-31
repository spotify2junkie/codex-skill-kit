---
name: verify-court-scan-bark
description: Verify the court-scan-bark Node CLI path from scanned court listings through evening filtering to a Bark payload with the original listing URL.
---

# Verify court-scan-bark

## Launch

This is a short-lived Node CLI; it has no server or build step. From the repository root, use Node.js 20 or newer and run each drive as its own process:

```sh
node packages/court-scan-bark/cli.mjs --input packages/court-scan-bark/fixtures/listings.json --from 2026-11-01 --through 2026-11-07
```

Readiness is a JSON array on stdout and exit code `0`. The CLI reads scan results from JSON, filters them, and prints Bark payloads. It does not fetch listings or send Bark requests. No teardown is needed for a completed process.

## Doctor

Run from the repository root:

```sh
node --version
node --input-type=module -e 'import { buildBarkPayload, filterEveningHits } from "./packages/court-scan-bark/index.mjs"; if (typeof buildBarkPayload !== "function" || typeof filterEveningHits !== "function") process.exit(1); process.stdout.write("court-scan-bark ready\n")'
```

Require Node.js 20 or newer and the `court-scan-bark ready` line before driving. If import fails, confirm the current directory is the repository root.

## Drive

Use the [feature map](./features/README.md), which lists the one user-facing path in this package.

## Evidence

Capture the exact command, input fixture path, stdout, stderr, and exit code. The proof must show that the early court is filtered out and that the retained Bark payload has `url` equal to the source listing URL. The successful run at `$HOME/ops/logs/poteto-24/court-scan-bark-dry-run.txt` is the reference format. Unit/property tests cover the 19:00 and 120-minute boundaries and missing URL rejection.

This dry-run produces a local payload only. It does not log in, order a court, access a network endpoint, or send Bark. Confirm this from the CLI implementation: it reads a local file and writes JSON to stdout.

## Cleanup

The CLI exits after printing its result and creates no processes, temporary files, or mutable application state. Keep evidence under `$HOME/ops/logs/poteto-24/`; do not remove it during cleanup.

## Helpers

The CLI is the verification helper. Invoke it with `node packages/court-scan-bark/cli.mjs --input <json-file> --from <YYYY-MM-DD> --through <YYYY-MM-DD>`.
