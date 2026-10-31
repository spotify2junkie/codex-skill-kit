const timePattern = /^(?:[01]\d|2[0-3]):[0-5]\d$/;
const datePattern = /^\d{4}-\d{2}-\d{2}$/;

function isDate(value) {
  if (typeof value !== "string" || !datePattern.test(value)) return false;
  const date = new Date(`${value}T00:00:00.000Z`);
  return !Number.isNaN(date.valueOf()) && date.toISOString().slice(0, 10) === value;
}

function minutesSinceMidnight(value) {
  if (typeof value !== "string" || !timePattern.test(value)) return null;
  const [hours, minutes] = value.split(":").map(Number);
  return hours * 60 + minutes;
}

export function durationMinutes(listing) {
  if (!listing || typeof listing !== "object") return null;
  if (Number.isFinite(listing.durationMinutes)) return listing.durationMinutes;
  const start = minutesSinceMidnight(listing.startTime);
  const end = minutesSinceMidnight(listing.endTime);
  if (start === null || end === null) return null;
  const elapsed = end - start;
  return elapsed < 0 ? elapsed + 24 * 60 : elapsed;
}

export function isEveningHit(listing, { from, through }) {
  if (!listing || !isDate(from) || !isDate(through) || from > through) return false;
  if (!isDate(listing.date) || listing.date < from || listing.date > through) return false;
  const start = minutesSinceMidnight(listing.startTime);
  if (start === null || start < 19 * 60) return false;
  if (durationMinutes(listing) < 120) return false;
  return typeof listing.surface === "string" && /^(wood|rubber)$/i.test(listing.surface.trim());
}

export function filterEveningHits(listings, window) {
  if (!Array.isArray(listings)) throw new TypeError("listings must be an array");
  return listings.filter((listing) => isEveningHit(listing, window));
}

export function buildBarkPayload(listing) {
  if (!listing || typeof listing.url !== "string" || listing.url.trim() === "") {
    throw new TypeError("listing.url is required");
  }
  let parsedUrl;
  try {
    parsedUrl = new URL(listing.url);
  } catch {
    throw new TypeError("listing.url must be an absolute URL");
  }
  if (!/^https?:$/.test(parsedUrl.protocol)) throw new TypeError("listing.url must use http or https");
  const venue = listing.venue?.trim() || "Court available";
  const duration = durationMinutes(listing);
  const durationText = duration === null ? "duration unavailable" : `${duration} minutes`;
  const location = listing.location?.trim();
  const title = `${venue} — ${listing.date} ${listing.startTime}`;
  const body = [
    `${listing.date} ${listing.startTime}${listing.endTime ? `–${listing.endTime}` : ""}`,
    `${durationText}; ${listing.surface} surface`,
    location,
  ].filter(Boolean).join("\n");
  return { title, body, url: listing.url };
}
