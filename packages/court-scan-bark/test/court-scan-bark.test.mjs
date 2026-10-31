import assert from "node:assert/strict";
import test from "node:test";
import { buildBarkPayload, filterEveningHits, isEveningHit } from "../index.mjs";

const window = { from: "2026-11-01", through: "2026-11-07" };
const listing = {
  date: "2026-11-03",
  startTime: "19:00",
  endTime: "21:00",
  durationMinutes: 120,
  surface: "wood",
  venue: "REA Central Court 2",
  location: "Central Singapore",
  url: "https://example.test/listings/rea-central-2",
};

test("Bark payload includes the source listing URL", () => {
  assert.deepEqual(buildBarkPayload(listing), {
    title: "REA Central Court 2 — 2026-11-03 19:00",
    body: "2026-11-03 19:00–21:00\n120 minutes; wood surface\nCentral Singapore",
    url: "https://example.test/listings/rea-central-2",
  });
});

test("building a Bark payload fails when the listing URL is missing", () => {
  const { url, ...withoutUrl } = listing;
  assert.equal(url, listing.url);
  assert.throws(() => buildBarkPayload(withoutUrl), /listing\.url is required/);
});

test("evening hit accepts inclusive date bounds and a two hour wood court", () => {
  assert.equal(isEveningHit(listing, window), true);
  assert.equal(isEveningHit({ ...listing, date: window.from }, window), true);
  assert.equal(isEveningHit({ ...listing, date: window.through }, window), true);
});

test("property: every valid pre-19:00 start is rejected", () => {
  for (let start = 0; start < 19 * 60; start += 1) {
    const hh = String(Math.floor(start / 60)).padStart(2, "0");
    const mm = String(start % 60).padStart(2, "0");
    assert.equal(isEveningHit({ ...listing, startTime: `${hh}:${mm}` }, window), false, `${hh}:${mm}`);
  }
});

test("property: every duration below two hours is rejected", () => {
  for (let minutes = -30; minutes < 120; minutes += 1) {
    assert.equal(isEveningHit({ ...listing, durationMinutes: minutes }, window), false, `${minutes} minutes`);
  }
});

test("filter returns only wood or rubber hits inside the date window", () => {
  const listings = [
    listing,
    { ...listing, url: "https://example.test/rubber", surface: "rubber" },
    { ...listing, url: "https://example.test/outside", date: "2026-11-08" },
    { ...listing, url: "https://example.test/concrete", surface: "concrete" },
  ];
  assert.deepEqual(filterEveningHits(listings, window), listings.slice(0, 2));
});
