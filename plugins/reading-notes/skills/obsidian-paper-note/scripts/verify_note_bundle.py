#!/usr/bin/env python3
"""Verify Obsidian embeds and the observable PDF invariants of a reading note."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


EMBED_RE = re.compile(r"!\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
ARTICLE_RE = re.compile(r"^##\s+(\d{2})\.\s+", re.MULTILINE)


def resolve_embed(note: Path, vault: Path, target: str) -> Path | None:
    for candidate in (note.parent / target, vault / target):
        if candidate.exists():
            return candidate.resolve()
    return None


def run_text(command: list[str]) -> str:
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "command failed: " + " ".join(command))
    return result.stdout


def check_pdf(path: Path, expected_pages: int, expected_cards: int) -> list[str]:
    errors: list[str] = []
    if not shutil.which("pdfinfo") or not shutil.which("pdftotext"):
        return ["pdfinfo and pdftotext are required for PDF verification"]

    info = run_text(["pdfinfo", str(path)])
    page_match = re.search(r"^Pages:\s+(\d+)$", info, re.MULTILINE)
    page_count = int(page_match.group(1)) if page_match else -1
    if page_count != expected_pages:
        errors.append(f"{path.name}: pages={page_count}, expected={expected_pages}")

    size_match = re.search(r"^Page size:\s+([\d.]+) x ([\d.]+) pts", info, re.MULTILINE)
    if not size_match:
        errors.append(f"{path.name}: Page size unavailable")
    else:
        width, height = map(float, size_match.groups())
        if abs(width - 595.0) > 2.0 or abs(height - 842.0) > 2.0:
            errors.append(f"{path.name}: not A4 ({width} x {height} pts)")

    text = run_text(["pdftotext", "-layout", str(path), "-"])
    for label in ("解决了什么", "代价是什么"):
        count = text.count(label)
        if count != expected_cards:
            errors.append(f"{path.name}: {label} count={count}, expected={expected_cards}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--note", required=True, type=Path)
    parser.add_argument("--vault-root", required=True, type=Path)
    parser.add_argument("--expected-articles", type=int)
    parser.add_argument("--expected-pdfs", type=int)
    parser.add_argument("--expected-pdf-pages", type=int, default=10)
    parser.add_argument("--expected-cards", type=int, default=10)
    parser.add_argument("--json-report", type=Path)
    args = parser.parse_args()

    note = args.note.expanduser().resolve()
    vault = args.vault_root.expanduser().resolve()
    errors: list[str] = []
    if not note.is_file():
        errors.append(f"note not found: {note}")
    if not vault.is_dir():
        errors.append(f"vault root not found: {vault}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    body = note.read_text(encoding="utf-8")
    if re.search(r"\{\{[^{}\n]+\}\}|\[TODO:[^\]]+\]", body):
        errors.append("unresolved scaffold placeholder found in Markdown")

    article_ids = ARTICLE_RE.findall(body)
    if args.expected_articles is not None and len(article_ids) != args.expected_articles:
        errors.append(f"article headings={len(article_ids)}, expected={args.expected_articles}")
    if args.expected_articles is not None:
        expected_ids = [f"{number:02d}" for number in range(1, args.expected_articles + 1)]
        if article_ids != expected_ids:
            errors.append("numbered article headings are duplicated, missing, or out of sequence")

    targets = EMBED_RE.findall(body)
    resolved: dict[str, Path] = {}
    for target in targets:
        path = resolve_embed(note, vault, target)
        if path is None:
            errors.append(f"missing embed: {target}")
        else:
            resolved[target] = path

    pdfs = sorted({path for path in resolved.values() if path.suffix.lower() == ".pdf"})
    if args.expected_pdfs is not None and len(pdfs) != args.expected_pdfs:
        errors.append(f"PDF embeds={len(pdfs)}, expected={args.expected_pdfs}")
    for pdf in pdfs:
        try:
            errors.extend(check_pdf(pdf, args.expected_pdf_pages, args.expected_cards))
        except RuntimeError as exc:
            errors.append(f"{pdf.name}: {exc}")

    report = {
        "note": str(note),
        "article_headings": len(article_ids),
        "embed_references": len(targets),
        "unique_resolved_embeds": len(set(resolved.values())),
        "pdfs_checked": len(pdfs),
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
    }
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
