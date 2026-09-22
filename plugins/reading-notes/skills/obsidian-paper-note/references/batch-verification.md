# Version-bound batch verification

Use for ranked combined notes, or when a previously accepted PDF is revised. Counts alone cannot detect a PDF attached to the wrong article. The parent owns final integration and acceptance; reviewers do not edit author assets.

## Authoritative state

Keep the confirmed selection ledger separate from the delivery manifest. Selection records why an article belongs; the delivery manifest binds the current note, sources, figures, PDF and review receipts. A historical PASS is not current acceptance. Regenerate after any render-input change; renew affected source review and all changed-page visual review, with prior unchanged-page coverage recorded explicitly. Review reports must distinguish current findings, superseded findings and unresolved findings. Never resolve an issue by just writing PASS into metadata.

Read every final PDF page across the review lanes. Check article identity, actual original-figure inclusion, module-to-card mapping, arrow semantics, Chinese glyphs, label overlap and page bounds. Review alternative branches and offline evaluation separately from runtime flow. XML-valid SVG and text extraction are not visual evidence. An original figure in an attachment directory does not prove it is in the PDF.

## Manifest v1

For ranked combined production, including revised PDFs inside that collection, `--manifest /absolute/path/bundle.json` is required for acceptance. The CLI keeps the flag optional only for compatibility with basic checks. Existing callers without a manifest get count/embed smoke checks, not full acceptance. This v1 schema is for numbered combined notes; standalone revisions need current source/visual evidence but must not be forced into fake numbered batches.

Top-level object: `schema_version: 1`, `articles: [...]`, in confirmed rank order. Every article has:

- `source_id`: nonempty stable identity, independent of rank; unique in this manifest.
- `rank`: two-digit rank string; unique, ordered and matched to the note's `## NN. Full title` heading.
- `title`, `canonical_url`: exact heading title and primary source URL, present in that article's section. This is a mapping check, not proof of semantic fidelity.
- `pdf`: path relative to note directory or vault root, same convention as an Obsidian embed. Exactly this one PDF must be embedded inside the corresponding article section; reject swapped or reused PDFs.
- `pdf_sha256`: SHA-256 of the actual final PDF.
- `inputs`: nonempty map from render/source input path to its SHA-256. These paths resolve relative to the manifest directory, or may be absolute. Include at least the per-article source content, architecture and renderer files actually used. The final combined note is checked separately, not a render input unless it truly was used to render.
- `cards`: positive integer expected concept-card count; do not invent cards merely to hit ten.
- `source_figure`: optional object with `path`, `sha256`, `pdf_page`. Input-path resolution applies; include the same path/hash in `inputs` so figure changes invalidate review receipts. Include when the primary source has a relevant architecture figure. The verifier checks file/hash and page range; visual review must prove that figure appears on that PDF page. A redraw is separately labeled, never passed off as the original.
- `reviews`: exactly one current receipt per lane `source` and `visual`. Each has `lane`, `reviewer`, `status`, `pdf_sha256`, `inputs`, `evidence`, `evidence_sha256`. Status must be `PASS` for acceptance; both PDF hash and the complete inputs map must equal this article's current values. Evidence paths resolve like inputs and must exist with matching hash. Use different reviewer identities for the two lanes. These are attestations, not cryptographic proof of independence or correctness.
- The visual receipt additionally has `pages_checked`, the full set of page numbers `1..actual_page_count`, and, when `source_figure` exists, `source_figure_page` equal to its `pdf_page`. Its report explains inherited unchanged-page coverage if a recheck did not reopen all pages.

Persist unresolved findings in the human-readable report. A receipt must not say PASS while its linked report retains an unresolved blocking finding. The verifier checks receipt consistency and hashes, not natural-language contradictions; the parent reads reports before delivery.

## Checks and limits

For a maximum-ten-page batch use:

```sh
python3 scripts/verify_note_bundle.py --note /absolute/master.md --vault-root /absolute/vault --expected-articles 20 --expected-pdfs 20 --max-pdf-pages 10 --manifest /absolute/bundle.json --json-report /absolute/qa.json
```

Use `--expected-pdf-pages 10 --expected-cards 10` only when exactly-ten was explicitly contracted. Without an exact page count the maximum defaults to ten; shorter PDFs are allowed. Card counts come from the manifest, an explicit CLI count, or balanced nonzero takeaway-label counts. Do not flag literal API templates such as `{{$userId}}` as unresolved scaffolds; detect explicit TODO markers instead.

Before final acceptance, compare the manifest's ranks, identities and score metadata with the confirmed selection ledger. The parent checks scores and confirmation; this PDF verifier does not decide what to select. Recheck current destination existence and local links, original retained-asset hashes, exact Markdown cardinality, and any superseded reports. If a vault is unavailable, report local completion separately from delivery. Never recreate an unavailable vault in another location or claim iCloud/native-app validation from filesystem checks.

When changing the verifier, run `python3 -m unittest discover -s scripts -p 'test_verify_note_bundle.py'` from the skill directory, then a read-only smoke check with real Poppler tools. Unit fixtures mock PDF extraction and cannot establish real rendering or visual quality.
