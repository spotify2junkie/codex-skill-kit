# Court scan and Bark verification map

This map covers the package's user-facing CLI flow from scanned listing JSON through evening filtering to a Bark payload. It uses only local fixture data and never sends Bark.

## Baseline preconditions

- Run from the repository root with Node.js 20 or newer.
- Use `packages/court-scan-bark/fixtures/listings.json` as local scan output.
- Require the date window `2026-11-01` through `2026-11-07`.
- Run the [doctor](../SKILL.md#doctor) first if the import or CLI behaves unexpectedly.
- Keep the source fixture unchanged during the run.

## Driving conventions

- Run the CLI as a fresh Node process.
- Save stdout, stderr, command, and exit code to the evidence path named by the verification skill.
- Confirm the eligible court payload's `url` equals the source listing URL.
- Do not configure credentials or invoke network services.

## Features

- [Scan, filter, and build Bark payload](./scan-filter-bark.md) covers the JSON input, date and evening filters, and the local Bark payload.
