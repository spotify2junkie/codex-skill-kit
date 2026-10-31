import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { buildBarkPayload, filterEveningHits } from "./index.mjs";

function optionsFrom(argv) {
  const options = {};
  for (let index = 0; index < argv.length; index += 1) {
    const key = argv[index];
    if (!["--input", "--from", "--through"].includes(key)) {
      throw new Error(`Unknown option: ${key}`);
    }
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) throw new Error(`Missing value for ${key}`);
    options[key.slice(2)] = value;
    index += 1;
  }
  for (const key of ["input", "from", "through"]) {
    if (!options[key]) throw new Error(`--${key} is required`);
  }
  return options;
}

export async function run(argv = process.argv.slice(2)) {
  const options = optionsFrom(argv);
  const listings = JSON.parse(await readFile(resolve(options.input), "utf8"));
  const hits = filterEveningHits(listings, { from: options.from, through: options.through });
  process.stdout.write(`${JSON.stringify(hits.map(buildBarkPayload), null, 2)}\n`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  run().catch((error) => {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 1;
  });
}
