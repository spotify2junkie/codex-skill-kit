# Scan, filter, and build Bark payload

The court scan path accepts listing results as JSON, keeps eligible evening wood or rubber courts, and prints one Bark payload for each hit with its listing URL.

## Sub-features

- `scan-json` reads the local JSON result from the court scan.
- `evening-filter` keeps listings inside the inclusive date window that start at or after 19:00 and last at least 120 minutes.
- `surface-filter` keeps wood and rubber courts.
- `bark-payload` prints a title, body, and required source listing URL without sending a notification.

## How to get to it (user POV)

- Run the package CLI on scanned court listings in JSON form.

## Driving it with the Node CLI

Preconditions:

- Current directory is the repository root.
- Node.js 20 or newer is available.
- The local fixture contains an eligible 19:00 wood court and an ineligible 18:30 rubber court.

- **Run the scan result through the filter.** Run `node packages/court-scan-bark/cli.mjs --input packages/court-scan-bark/fixtures/listings.json --from 2026-11-01 --through 2026-11-07`. Exit code is `0`; stdout contains one payload for `REA Central Court 2`.
- **Check the source link.** Inspect that payload's `url` field. It equals `https://example.test/listings/rea-central-2`, the `url` value in the input listing.
- **Check the filter.** The output does not contain `Early Court`, whose listing starts at 18:30.
- **Check the action boundary.** The command only reads the fixture and prints JSON; no credentials, network calls, orders, or Bark sends occur.
- **Proof.** Save the literal command, input path, stdout, stderr, and exit code. `$HOME/ops/logs/poteto-24/court-scan-bark-dry-run.txt` is the completed proof for this fixture.

## Gotchas

- The date window is inclusive and uses ISO dates.
- Start times use 24-hour `HH:MM` local listing time.
- Duration can be supplied as `durationMinutes` or derived from `startTime` and `endTime`.
- A missing, relative, or non-HTTP(S) listing URL prevents payload construction.
- A successful dry-run prints a payload; it does not mean Bark received it.
