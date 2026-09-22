#!/usr/bin/env python3
"""Verify Obsidian embeds and the observable PDF invariants of a reading note.

The verifier has two intentionally different modes:

* Basic mode (the default) checks Markdown embeds and inexpensive PDF
  invariants. PDFs may be shorter than the default ten-page maximum.
* Manifest mode (``--manifest``) additionally checks the version-bound
  delivery manifest described in ``references/batch-verification.md``.

The script is deliberately conservative about what it can claim. It checks
hashes, paths, page ranges and receipt consistency; it does not claim to have
performed visual review of a PDF page.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


EMBED_RE = re.compile(r"!\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
ARTICLE_RE = re.compile(r"^##\s+(\d{2})\.\s+", re.MULTILINE)
ARTICLE_HEADING_RE = re.compile(
    r"^##\s+(\d{2})\.\s+([^\n]+?)\s*$", re.MULTILINE
)
HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")
URL_BOUNDARY_CHARS = r"A-Za-z0-9._~:/?#\[\]@!$&'*+,;=%-"


def resolve_embed(note: Path, vault: Path, target: str) -> Path | None:
    """Resolve an Obsidian embed using note-relative then vault-relative paths."""

    try:
        target_path = Path(target).expanduser()
    except (OSError, RuntimeError, ValueError):
        return None
    candidates = (
        (target_path,)
        if target_path.is_absolute()
        else (note.parent / target_path, vault / target_path)
    )
    for candidate in candidates:
        try:
            if candidate.exists():
                return candidate.resolve()
        except (OSError, RuntimeError, ValueError):
            # A broken path should become a verification error, not a traceback.
            continue
    return None


def _manifest_path(manifest_dir: Path, value: str) -> Path:
    """Return the manifest-relative path convention used by v1 fields."""

    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (manifest_dir / path).resolve()


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _valid_hash(value: Any) -> bool:
    return isinstance(value, str) and HASH_RE.fullmatch(value) is not None


def run_text(command: list[str]) -> str:
    """Run a text command and turn all expected process failures into RuntimeError."""

    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    except OSError as exc:
        raise RuntimeError(str(exc)) from exc
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "command failed: " + " ".join(command))
    return result.stdout


def inspect_pdf(path: Path) -> tuple[list[str], int, str]:
    """Return ``(errors, page_count, extracted_text)`` for one PDF."""

    errors: list[str] = []
    page_count = -1
    text = ""
    if not path.is_file():
        return [f"{path.name}: PDF not found"], page_count, text
    if not shutil.which("pdfinfo") or not shutil.which("pdftotext"):
        return ["pdfinfo and pdftotext are required for PDF verification"], page_count, text

    try:
        info = run_text(["pdfinfo", str(path)])
    except RuntimeError as exc:
        errors.append(f"{path.name}: {exc}")
        info = ""

    page_match = re.search(r"^Pages:\s+(\d+)\s*$", info, re.MULTILINE)
    if page_match:
        page_count = int(page_match.group(1))
    else:
        errors.append(f"{path.name}: page count unavailable")

    size_match = re.search(r"^Page size:\s+([\d.]+) x ([\d.]+) pts", info, re.MULTILINE)
    if not size_match:
        errors.append(f"{path.name}: Page size unavailable")
    else:
        width, height = map(float, size_match.groups())
        if abs(width - 595.0) > 2.0 or abs(height - 842.0) > 2.0:
            errors.append(f"{path.name}: not A4 ({width} x {height} pts)")

    try:
        text = run_text(["pdftotext", "-layout", str(path), "-"])
    except RuntimeError as exc:
        errors.append(f"{path.name}: {exc}")
    return errors, page_count, text


def check_pdf(
    path: Path,
    expected_pages: int | None,
    expected_cards: int | None,
    max_pages: int | None = 10,
) -> list[str]:
    """Check one PDF.

    ``expected_pages`` is an explicit exact-page contract. When it is omitted,
    ``max_pages`` is an upper bound and shorter PDFs pass. Keeping the exact
    argument preserves the old command-line API for callers that explicitly
    requested ten pages.
    """

    errors, page_count, text = inspect_pdf(path)
    if page_count >= 0:
        if expected_pages is not None and page_count != expected_pages:
            errors.append(f"{path.name}: pages={page_count}, expected={expected_pages}")
        elif max_pages is not None and page_count > max_pages:
            errors.append(f"{path.name}: pages={page_count}, maximum={max_pages}")

    counts = [text.count(label) for label in ("解决了什么", "代价是什么")]
    if expected_cards is not None:
        for label, count in zip(("解决了什么", "代价是什么"), counts):
            if count != expected_cards:
                errors.append(f"{path.name}: {label} count={count}, expected={expected_cards}")
    elif counts[0] == 0 or counts[1] == 0 or counts[0] != counts[1]:
        errors.append(
            f"{path.name}: takeaway label counts are not balanced and nonzero "
            f"(解决了什么={counts[0]}, 代价是什么={counts[1]})"
        )
    return errors


def _article_sections(body: str) -> list[tuple[str, str, str]]:
    matches = list(ARTICLE_HEADING_RE.finditer(body))
    sections: list[tuple[str, str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections.append((match.group(1), match.group(2).strip(), body[match.start() : end]))
    return sections


def _contains_exact_url(section: str, url: str) -> bool:
    """Match a URL token, not a URL that merely contains the requested prefix."""

    pattern = rf"(?<![{URL_BOUNDARY_CHARS}]){re.escape(url)}(?![{URL_BOUNDARY_CHARS}])"
    return re.search(pattern, section) is not None


def _error_field(errors: list[str], context: str, message: str) -> None:
    errors.append(f"{context}: {message}")


def _require_string(
    value: Any, field: str, context: str, errors: list[str], *, nonempty: bool = True
) -> str | None:
    if not isinstance(value, str) or (nonempty and not value.strip()):
        _error_field(errors, context, f"{field} must be a nonempty string")
        return None
    return value


def _check_hash_path(
    value: Any,
    expected_hash: Any,
    manifest_dir: Path,
    context: str,
    errors: list[str],
) -> Path | None:
    path_value = _require_string(value, "path", context, errors)
    if path_value is None:
        return None
    if not _valid_hash(expected_hash):
        _error_field(errors, context, "sha256 must be a 64-character hexadecimal hash")
    path = _manifest_path(manifest_dir, path_value)
    if not path.is_file():
        _error_field(errors, context, f"missing file: {path_value}")
        return path
    if _valid_hash(expected_hash):
        try:
            actual_hash = _hash_file(path)
        except OSError as exc:
            _error_field(errors, context, f"cannot hash {path_value}: {exc}")
        else:
            if actual_hash.lower() != str(expected_hash).lower():
                _error_field(
                    errors,
                    context,
                    f"hash mismatch for {path_value}: actual={actual_hash}, expected={expected_hash}",
                )
    return path


def _normalise_hash_map(value: Any, field: str, context: str, errors: list[str]) -> dict[str, str] | None:
    if not isinstance(value, dict) or not value:
        _error_field(errors, context, f"{field} must be a nonempty object of path -> sha256")
        return None
    result: dict[str, str] = {}
    for path, digest in value.items():
        if not isinstance(path, str) or not path.strip():
            _error_field(errors, context, f"{field} has a non-string path")
            continue
        if not _valid_hash(digest):
            _error_field(errors, context, f"{field}[{path!r}] is not a SHA-256 hash")
            continue
        result[path] = digest
    return result


def _check_input_map(
    value: Any,
    manifest_dir: Path,
    context: str,
    errors: list[str],
) -> dict[str, str] | None:
    mapping = _normalise_hash_map(value, "inputs", context, errors)
    if mapping is None:
        return None
    for path_value, expected_hash in mapping.items():
        path = _manifest_path(manifest_dir, path_value)
        if not path.is_file():
            _error_field(errors, context, f"missing input: {path_value}")
            continue
        try:
            actual_hash = _hash_file(path)
        except OSError as exc:
            _error_field(errors, context, f"cannot hash input {path_value}: {exc}")
            continue
        if actual_hash.lower() != expected_hash.lower():
            _error_field(
                errors,
                context,
                f"input hash mismatch for {path_value}: actual={actual_hash}, expected={expected_hash}",
            )
    return mapping


def _evidence_items(review: dict[str, Any], context: str, errors: list[str]) -> list[tuple[str, str]]:
    """Normalise v1 evidence fields while accepting a useful list form."""

    evidence = review.get("evidence")
    evidence_hash = review.get("evidence_sha256")
    if isinstance(evidence, str):
        evidence_values = [evidence]
    elif isinstance(evidence, list) and all(isinstance(item, str) for item in evidence):
        evidence_values = evidence
    elif isinstance(evidence, dict) and all(isinstance(item, str) for item in evidence):
        # A map form is convenient for reports and remains unambiguous.
        evidence_values = list(evidence.keys())
        if evidence_hash is None:
            evidence_hash = evidence
    else:
        _error_field(errors, context, "evidence must be a path, list of paths, or path -> hash object")
        return []

    if isinstance(evidence_hash, str):
        hash_values = [evidence_hash]
    elif isinstance(evidence_hash, list) and all(isinstance(item, str) for item in evidence_hash):
        hash_values = evidence_hash
    elif isinstance(evidence_hash, dict):
        hash_values = [evidence_hash.get(item) for item in evidence_values]
    else:
        _error_field(errors, context, "evidence_sha256 must be a hash, list, or path -> hash object")
        return []

    if len(evidence_values) != len(hash_values) or not evidence_values:
        _error_field(errors, context, "evidence and evidence_sha256 must contain the same nonzero paths")
        return []
    pairs: list[tuple[str, str]] = []
    for path_value, digest in zip(evidence_values, hash_values):
        if not isinstance(path_value, str) or not path_value.strip() or not _valid_hash(digest):
            _error_field(errors, context, "evidence paths and hashes must be nonempty and valid")
            continue
        pairs.append((path_value, digest))
    return pairs


def _check_review_evidence(
    review: dict[str, Any], manifest_dir: Path, context: str, errors: list[str]
) -> None:
    for path_value, expected_hash in _evidence_items(review, context, errors):
        path = _manifest_path(manifest_dir, path_value)
        if not path.is_file():
            _error_field(errors, context, f"missing evidence report: {path_value}")
            continue
        try:
            actual_hash = _hash_file(path)
        except OSError as exc:
            _error_field(errors, context, f"cannot hash evidence {path_value}: {exc}")
            continue
        if actual_hash.lower() != expected_hash.lower():
            _error_field(
                errors,
                context,
                f"evidence hash mismatch for {path_value}: actual={actual_hash}, expected={expected_hash}",
            )


def _validate_manifest(
    manifest_path: Path,
    note: Path,
    vault: Path,
    body: str,
    sections: list[tuple[str, str, str]],
    errors: list[str],
    max_pages: int | None = 10,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Validate manifest v1 and return articles plus actual PDF page counts."""

    stats = {"manifest_articles": 0, "manifest_pdfs_checked": 0}
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"manifest error: {exc}")
        return [], stats

    if not isinstance(raw, dict):
        errors.append("manifest error: top-level value must be an object")
        return [], stats
    if isinstance(raw.get("schema_version"), bool) or raw.get("schema_version") != 1:
        errors.append("manifest error: schema_version must be 1")
    raw_articles = raw.get("articles")
    if not isinstance(raw_articles, list):
        errors.append("manifest error: articles must be a list")
        return [], stats

    manifest_dir = manifest_path.parent
    articles: list[dict[str, Any]] = []
    seen_source_ids: set[str] = set()
    seen_ranks: set[str] = set()
    seen_pdf_paths: dict[Path, str] = {}
    actual_page_counts: dict[str, int] = {}
    if not raw_articles:
        errors.append("manifest error: articles must not be empty")

    for index, item in enumerate(raw_articles, start=1):
        context = f"manifest article {index}"
        if not isinstance(item, dict):
            _error_field(errors, context, "article must be an object")
            continue
        source_id = _require_string(item.get("source_id"), "source_id", context, errors)
        rank = _require_string(item.get("rank"), "rank", context, errors)
        title = _require_string(item.get("title"), "title", context, errors)
        canonical_url = _require_string(item.get("canonical_url"), "canonical_url", context, errors)
        pdf_value = _require_string(item.get("pdf"), "pdf", context, errors)
        pdf_hash = item.get("pdf_sha256")
        if source_id is not None:
            if source_id in seen_source_ids:
                _error_field(errors, context, f"duplicate source_id: {source_id}")
            seen_source_ids.add(source_id)
        if rank is not None:
            if not re.fullmatch(r"\d{2}", rank):
                _error_field(errors, context, "rank must be a two-digit string")
            if rank in seen_ranks:
                _error_field(errors, context, f"duplicate rank: {rank}")
            seen_ranks.add(rank)
        if not _valid_hash(pdf_hash):
            _error_field(errors, context, "pdf_sha256 must be a 64-character hexadecimal hash")
        cards = item.get("cards")
        if not isinstance(cards, int) or isinstance(cards, bool) or cards <= 0:
            _error_field(errors, context, "cards must be a positive integer")

        inputs = _check_input_map(item.get("inputs"), manifest_dir, context, errors)
        pdf_path: Path | None = None
        if pdf_value is not None:
            pdf_path = resolve_embed(note, vault, pdf_value)
            if pdf_path is None:
                _error_field(errors, context, f"missing PDF: {pdf_value}")
            else:
                prior = seen_pdf_paths.get(pdf_path)
                if prior is not None:
                    _error_field(errors, context, f"PDF is reused/swapped with article {prior}: {pdf_value}")
                else:
                    seen_pdf_paths[pdf_path] = rank or str(index)
                stats["manifest_pdfs_checked"] += 1
                try:
                    actual_hash = _hash_file(pdf_path)
                except OSError as exc:
                    _error_field(errors, context, f"cannot hash PDF {pdf_value}: {exc}")
                else:
                    if _valid_hash(pdf_hash) and actual_hash.lower() != str(pdf_hash).lower():
                        _error_field(
                            errors,
                            context,
                            f"PDF hash mismatch: actual={actual_hash}, expected={pdf_hash}",
                        )
                pdf_errors, page_count, pdf_text = inspect_pdf(pdf_path)
                errors.extend(f"{context}: {message}" for message in pdf_errors)
                actual_page_counts[source_id or str(index)] = page_count
                if isinstance(cards, int) and not isinstance(cards, bool):
                    for label in ("解决了什么", "代价是什么"):
                        count = pdf_text.count(label)
                        if count != cards:
                            _error_field(errors, context, f"{label} count={count}, expected={cards}")
                if max_pages is not None and page_count > max_pages:
                    _error_field(errors, context, f"PDF pages={page_count}, maximum={max_pages}")

        source_figure = item.get("source_figure")
        source_figure_page: int | None = None
        if source_figure is not None:
            if not isinstance(source_figure, dict):
                _error_field(errors, context, "source_figure must be an object")
            else:
                source_figure_page = source_figure.get("pdf_page")
                source_figure_path_value = source_figure.get("path")
                source_figure_hash = source_figure.get("sha256")
                _check_hash_path(
                    source_figure_path_value,
                    source_figure_hash,
                    manifest_dir,
                    context + ".source_figure",
                    errors,
                )
                # An original figure is itself a render input. Requiring the
                # same path/hash in the article input map makes a figure
                # mutation stale the source and visual receipts as well.
                if inputs is not None and isinstance(source_figure_path_value, str) and _valid_hash(source_figure_hash):
                    figure_path = _manifest_path(manifest_dir, source_figure_path_value)
                    included = any(
                        _manifest_path(manifest_dir, input_path) == figure_path
                        and digest.lower() == str(source_figure_hash).lower()
                        for input_path, digest in inputs.items()
                    )
                    if not included:
                        _error_field(errors, context, "source_figure path/hash must be present in inputs")
                if not isinstance(source_figure_page, int) or isinstance(source_figure_page, bool) or source_figure_page < 1:
                    _error_field(errors, context, "source_figure.pdf_page must be a positive integer")
                elif source_id is not None and actual_page_counts.get(source_id, -1) >= 0 and source_figure_page > actual_page_counts[source_id]:
                    _error_field(errors, context, "source_figure.pdf_page is outside the PDF page range")

        reviews = item.get("reviews")
        lane_reviews: dict[str, dict[str, Any]] = {}
        if not isinstance(reviews, list) or len(reviews) != 2:
            _error_field(errors, context, "reviews must contain exactly one source and one visual receipt")
        else:
            for review_index, review in enumerate(reviews, start=1):
                review_context = f"{context}.review {review_index}"
                if not isinstance(review, dict):
                    _error_field(errors, review_context, "review must be an object")
                    continue
                lane = _require_string(review.get("lane"), "lane", review_context, errors)
                reviewer = _require_string(review.get("reviewer"), "reviewer", review_context, errors)
                status = review.get("status")
                if status != "PASS":
                    _error_field(errors, review_context, "status must be PASS for acceptance")
                if lane not in {"source", "visual"}:
                    _error_field(errors, review_context, "lane must be source or visual")
                elif lane in lane_reviews:
                    _error_field(errors, review_context, f"duplicate review lane: {lane}")
                else:
                    lane_reviews[lane] = review
                review_pdf_hash = review.get("pdf_sha256")
                if not _valid_hash(review_pdf_hash):
                    _error_field(errors, review_context, "pdf_sha256 must be a SHA-256 hash")
                elif _valid_hash(pdf_hash) and str(review_pdf_hash).lower() != str(pdf_hash).lower():
                    _error_field(errors, review_context, "pdf_sha256 does not match article PDF hash")
                review_inputs = _normalise_hash_map(review.get("inputs"), "inputs", review_context, errors)
                if inputs is not None and review_inputs is not None and review_inputs != inputs:
                    _error_field(errors, review_context, "inputs do not match the article's current inputs")
                _check_review_evidence(review, manifest_dir, review_context, errors)
                if lane == "visual":
                    pages_checked = review.get("pages_checked")
                    page_count = actual_page_counts.get(source_id or str(index), -1)
                    if not isinstance(pages_checked, list) or any(
                        not isinstance(page, int) or isinstance(page, bool) for page in pages_checked
                    ):
                        _error_field(errors, review_context, "pages_checked must be a list of page numbers")
                    elif page_count >= 0 and sorted(set(pages_checked)) != list(range(1, page_count + 1)):
                        _error_field(
                            errors,
                            review_context,
                            f"pages_checked must cover every actual page 1..{page_count}",
                        )
                    if source_figure_page is not None and review.get("source_figure_page") != source_figure_page:
                        _error_field(errors, review_context, "source_figure_page does not match source_figure.pdf_page")

        source_reviewer = lane_reviews.get("source", {}).get("reviewer")
        visual_reviewer = lane_reviews.get("visual", {}).get("reviewer")
        if source_reviewer and visual_reviewer and source_reviewer == visual_reviewer:
            _error_field(errors, context, "source and visual reviewers must be different identities")

        if rank is not None and title is not None and canonical_url is not None:
            articles.append(item)

    stats["manifest_articles"] = len(raw_articles)
    ranks = [item.get("rank") for item in articles if isinstance(item.get("rank"), str)]
    if ranks != sorted(ranks):
        errors.append("manifest error: articles are not in rank order")
    if len(articles) != len(sections):
        errors.append(f"manifest article count={len(articles)}, note sections={len(sections)}")

    # Match identity, title, URL and PDF embed within the exact corresponding section.
    if len(articles) == len(sections):
        embedded_paths: dict[Path, str] = {}
        for item, (section_rank, section_title, section_body) in zip(articles, sections):
            context = f"manifest article {item.get('rank', '?')}"
            rank = item.get("rank")
            if section_rank != rank:
                _error_field(errors, context, f"note heading rank={section_rank!r} does not match manifest rank={rank!r}")
            if section_title != item.get("title"):
                _error_field(errors, context, "note heading title does not exactly match manifest title")
            canonical_url = item.get("canonical_url")
            if isinstance(canonical_url, str) and not _contains_exact_url(section_body, canonical_url):
                _error_field(errors, context, "canonical_url is not present in the corresponding article section")
            targets = EMBED_RE.findall(section_body)
            section_pdf_targets = [target for target in targets if target.lower().endswith(".pdf")]
            expected_pdf = item.get("pdf")
            expected_path = resolve_embed(note, vault, expected_pdf) if isinstance(expected_pdf, str) else None
            matching = [resolve_embed(note, vault, target) for target in section_pdf_targets]
            matching_existing = [path for path in matching if path is not None]
            if expected_path is None or sum(path == expected_path for path in matching_existing) != 1:
                _error_field(errors, context, "the manifest PDF must be embedded exactly once in its article section")
            if len(section_pdf_targets) != 1:
                _error_field(errors, context, "article section must contain exactly one PDF embed")
            for path in matching_existing:
                prior = embedded_paths.get(path)
                if prior is not None:
                    _error_field(errors, context, f"PDF embed is reused/swapped with article {prior}")
                else:
                    embedded_paths[path] = str(rank)

    return articles, actual_page_counts


def _make_report(
    note: Path,
    article_ids: list[str],
    targets: list[str],
    resolved: dict[str, Path],
    pdfs: list[Path],
    errors: list[str],
    manifest: Path | None = None,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "note": str(note),
        "article_headings": len(article_ids),
        "embed_references": len(targets),
        "unique_resolved_embeds": len(set(resolved.values())),
        "pdfs_checked": len(pdfs),
        "verification_level": "manifest_consistency" if manifest is not None else "basic",
        "limitations": [
            "Checks Markdown paths, hashes, PDF metadata and extracted labels; it is not semantic or visual proof."
        ],
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
    }
    if manifest is not None:
        report["manifest"] = str(manifest)
    return report


def _write_and_print_report(report: dict[str, Any], report_path: Path | None) -> None:
    if report_path is not None:
        try:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except OSError as exc:
            # The requested report path is part of the observable interface. A
            # failed write is represented in stdout rather than raising.
            report.setdefault("errors", []).append(f"could not write JSON report: {exc}")
            report["status"] = "FAIL"
    print(json.dumps(report, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--note", required=True, type=Path)
    parser.add_argument("--vault-root", required=True, type=Path)
    parser.add_argument("--expected-articles", type=int)
    parser.add_argument("--expected-pdfs", type=int)
    parser.add_argument(
        "--expected-pdf-pages",
        type=int,
        help="require this exact PDF page count (legacy exact-count mode)",
    )
    parser.add_argument(
        "--max-pdf-pages",
        type=int,
        default=None,
        help="maximum PDF page count when no exact count is requested (default: 10)",
    )
    parser.add_argument("--expected-cards", type=int)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--json-report", type=Path)
    args = parser.parse_args(argv)

    errors: list[str] = []

    def cli_path(value: Path | None, label: str) -> Path | None:
        if value is None:
            return None
        try:
            return value.expanduser().resolve()
        except (OSError, RuntimeError, ValueError) as exc:
            errors.append(f"invalid {label} path: {exc}")
            return None

    note = cli_path(args.note, "note")
    vault = cli_path(args.vault_root, "vault")
    manifest = cli_path(args.manifest, "manifest")
    report_path = cli_path(args.json_report, "report")
    if errors:
        report = _make_report(args.note, [], [], {}, [], errors, args.manifest)
        _write_and_print_report(report, report_path)
        return 1
    assert note is not None and vault is not None
    # The historical exact-page flag is allowed to request a value above ten.
    # A maximum is implicit only when no exact count was requested; if callers
    # spell both flags, report the ambiguity instead of silently choosing one.
    max_pages = args.max_pdf_pages if args.max_pdf_pages is not None else (
        None if args.expected_pdf_pages is not None else 10
    )
    article_ids: list[str] = []
    targets: list[str] = []
    resolved: dict[str, Path] = {}
    pdfs: list[Path] = []

    if not note.is_file():
        errors.append(f"note not found: {note}")
    if not vault.is_dir():
        errors.append(f"vault root not found: {vault}")
    if manifest is not None and not manifest.is_file():
        errors.append(f"manifest not found: {manifest}")
    if args.expected_pdf_pages is not None and args.max_pdf_pages is not None:
        errors.append("--expected-pdf-pages and --max-pdf-pages are conflicting flags; choose one")

    body = ""
    body_read_ok = False
    if not errors or note.is_file():
        try:
            body = note.read_text(encoding="utf-8")
            body_read_ok = True
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"cannot read note: {exc}")

    if body_read_ok:
        if not body.strip():
            errors.append("note is empty or whitespace-only")
        # Deliberately flag explicit TODO markers only. Literal API templates
        # such as {{$userId}} are content, not unresolved scaffolding.
        if re.search(r"(?i)\[\s*TODO\s*:|<!--\s*TODO\s*:", body):
            errors.append("unresolved TODO marker found in Markdown")

        article_ids = ARTICLE_RE.findall(body)
        if args.expected_articles is not None and len(article_ids) != args.expected_articles:
            errors.append(f"article headings={len(article_ids)}, expected={args.expected_articles}")
        if args.expected_articles is not None:
            expected_ids = [f"{number:02d}" for number in range(1, args.expected_articles + 1)]
            if article_ids != expected_ids:
                errors.append("numbered article headings are duplicated, missing, or out of sequence")

        targets = EMBED_RE.findall(body)
        for target in targets:
            path = resolve_embed(note, vault, target)
            if path is None:
                errors.append(f"missing embed: {target}")
            else:
                resolved[target] = path

        pdfs = sorted({path for path in resolved.values() if path.suffix.lower() == ".pdf"}, key=str)
        if args.expected_pdfs is not None and len(pdfs) != args.expected_pdfs:
            errors.append(f"PDF embeds={len(pdfs)}, expected={args.expected_pdfs}")
        for pdf in pdfs:
            errors.extend(check_pdf(pdf, args.expected_pdf_pages, args.expected_cards, max_pages))

        sections = _article_sections(body)
        if manifest is not None and manifest.is_file():
            try:
                _validate_manifest(manifest, note, vault, body, sections, errors, max_pages)
            except (OSError, RuntimeError, ValueError) as exc:
                errors.append(f"manifest validation error: {exc}")

    report = _make_report(note, article_ids, targets, resolved, pdfs, errors, manifest)
    _write_and_print_report(report, report_path)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
