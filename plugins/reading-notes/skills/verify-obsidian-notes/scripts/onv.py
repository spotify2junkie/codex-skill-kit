#!/usr/bin/env python3
"""Verify an Obsidian engineering reading note and its embedded ELI5 PDF."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


REQUIRED_COMMANDS = ("pdfinfo", "pdftotext", "pdftoppm", "magick")
IMAGE_EXTENSIONS = ("png", "jpg", "jpeg", "webp", "svg")


def fail(message: str, code: int = 1) -> None:
    print(f"ONV_ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, text=True, capture_output=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def absolute(path: str) -> Path:
    return Path(path).expanduser().resolve()


def within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def doctor(args: argparse.Namespace) -> int:
    note = absolute(args.note)
    vault_root = absolute(args.vault_root)
    problems: list[str] = []
    if not note.is_file():
        problems.append(f"note not found: {note}")
    if not vault_root.is_dir():
        problems.append(f"vault root not found: {vault_root}")
    if note.exists() and vault_root.exists() and not within(note, vault_root):
        problems.append(f"note is outside vault root: {note}")
    commands = {name: shutil.which(name) for name in REQUIRED_COMMANDS}
    for name, path in commands.items():
        if not path:
            problems.append(f"required command missing: {name}")
    payload = {
        "note": str(note),
        "vault_root": str(vault_root),
        "python": sys.version.split()[0],
        "commands": commands,
        "problems": problems,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if problems:
        print("ONV_DOCTOR_FAIL")
        return 1
    print("ONV_DOCTOR_OK")
    return 0


def article_section(markdown: str, article: str | None) -> tuple[str, str]:
    matches = list(re.finditer(r"(?m)^#{1,2}\s+(\d{2})\.\s+([^\n]+)$", markdown))
    if article:
        match = next((item for item in matches if item.group(1) == article.zfill(2)), None)
        if not match:
            fail(f"article {article} not found in note")
        end = next((item.start() for item in matches if item.start() > match.start()), len(markdown))
        return match.group(1), markdown[match.start():end]
    if len(matches) > 1:
        fail("note contains multiple numbered articles; pass --article NN")
    if matches:
        return matches[0].group(1), markdown[matches[0].start():]
    return "single", markdown


def wiki_embeds(section: str, extension_pattern: str) -> list[str]:
    pattern = rf"!\[\[([^\]|#]+\.(?:{extension_pattern}))(?:[|#][^\]]*)?\]\]"
    return re.findall(pattern, section, flags=re.IGNORECASE)


def resolve_wikilink(target: str, note: Path, vault_root: Path) -> Path | None:
    target = target.strip().replace("\\", "/")
    candidates = [vault_root / target, note.parent / target]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    suffix = target.casefold()
    matches = [
        path.resolve()
        for path in vault_root.rglob(Path(target).name)
        if path.is_file() and path.as_posix().casefold().endswith(suffix)
    ]
    unique = list(dict.fromkeys(matches))
    return unique[0] if len(unique) == 1 else None


def add_check(checks: list[dict[str, Any]], check_id: str, passed: bool, detail: str) -> None:
    checks.append({"id": check_id, "status": "pass" if passed else "fail", "detail": detail})


def has_all(text: str, values: tuple[str, ...]) -> bool:
    lowered = text.casefold()
    return all(value.casefold() in lowered for value in values)


def has_any(text: str, values: tuple[str, ...]) -> bool:
    lowered = text.casefold()
    return any(value.casefold() in lowered for value in values)


def parse_pdfinfo(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def render_pdf(pdf: Path, evidence: Path) -> tuple[list[Path], Path]:
    prefix = evidence / "page"
    run(["pdftoppm", "-png", "-r", "120", str(pdf), str(prefix)])
    pages = sorted(evidence.glob("page-*.png"))
    if not pages:
        fail("pdftoppm produced no pages")
    contact = evidence / "contact-sheet.png"
    command = [
        "magick",
        "montage",
        *[str(path) for path in pages],
        "-thumbnail",
        "320x",
        "-tile",
        "2x",
        "-geometry",
        "+12+18",
        "-background",
        "#e8e3d8",
        str(contact),
    ]
    run(command)
    return pages, contact


def verify(args: argparse.Namespace) -> int:
    note = absolute(args.note)
    vault_root = absolute(args.vault_root)
    run_dir = absolute(args.run_dir)
    if run_dir.exists() and any(run_dir.iterdir()):
        fail(f"run directory is not empty; choose a new isolated path: {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=True)
    evidence = run_dir / "evidence"
    scratch = run_dir / "scratch"
    evidence.mkdir()
    scratch.mkdir()

    if not note.is_file() or not vault_root.is_dir() or not within(note, vault_root):
        fail("doctor preconditions are not met; run doctor first")
    for command in REQUIRED_COMMANDS:
        if not shutil.which(command):
            fail(f"required command missing: {command}")

    markdown = note.read_text(encoding="utf-8")
    article_id, section = article_section(markdown, args.article)
    checks: list[dict[str, Any]] = []

    note_groups = {
        "note.article_info": ("文章信息", "来源"),
        "note.conclusion": ("一句话结论",),
        "note.main_flow": ("主线图",),
        "note.relevance": ("为什么和我有关",),
        "note.framework": ("架构", "数据流"),
        "note.evidence_boundary": ("证据", "边界"),
        "note.migration": ("迁移",),
        "note.fact_check": ("事实核对",),
        "note.insight": ("Insight", "反直觉"),
    }
    for check_id, tokens in note_groups.items():
        add_check(checks, check_id, has_all(section, tokens), f"required tokens: {', '.join(tokens)}")

    add_check(
        checks,
        "note.framework_io",
        has_all(section, ("输入", "操作", "输出", "下游")),
        "framework explains input, operation, output, and downstream",
    )
    critical_groups = {
        "facts": ("计算事实", "论文直接可核对", "事实层"),
        "author": ("作者解释", "作者自报", "作者称", "作者报告"),
        "unproved": ("尚未证明", "未证明", "未公开", "未披露"),
        "shortcut": ("shortcut", "捷径"),
        "falsifiable_migration": ("最小实验", "实验假设", "独立回放", "holdout"),
    }
    for name, alternatives in critical_groups.items():
        add_check(
            checks,
            f"note.critical.{name}",
            has_any(section, alternatives),
            f"one of: {', '.join(alternatives)}",
        )
    production_boundary = has_any(section, ("人工复核", "人审", "规则或人工")) and has_any(
        section, ("处置", "封禁", "拦截", "最终动作")
    )
    add_check(
        checks,
        "note.production_boundary",
        production_boundary,
        "consequential action remains behind rules or human review",
    )
    training_contract = has_any(section, ("训练账单", "Loss 账单", "Reward", "Objective", "无训练 Loss"))
    add_check(checks, "note.training_ledger", training_contract, "training objective or explicit absence is recorded")

    pdf_targets = wiki_embeds(section, "pdf")
    image_targets = wiki_embeds(section, "|".join(IMAGE_EXTENSIONS))
    add_check(checks, "note.pdf_embed_count", len(pdf_targets) == 1, f"embedded PDF count: {len(pdf_targets)}")
    add_check(checks, "note.figure_embed", bool(image_targets), f"embedded framework images: {len(image_targets)}")

    pdf = resolve_wikilink(pdf_targets[0], note, vault_root) if len(pdf_targets) == 1 else None
    figures = [resolve_wikilink(target, note, vault_root) for target in image_targets]
    add_check(checks, "note.pdf_resolves", pdf is not None, str(pdf or pdf_targets[:1]))
    add_check(
        checks,
        "note.figure_resolves",
        bool(figures) and all(figures),
        ", ".join(str(path) for path in figures) if figures else "no figure",
    )
    provenance = has_any(section, ("原文 Figure", "原图", "教学重绘", "原文未提供可核验架构图"))
    add_check(checks, "note.figure_provenance", provenance, "framework figure provenance is explicit")

    pdf_meta: dict[str, Any] = {}
    pdf_text = ""
    rendered_pages: list[Path] = []
    contact: Path | None = None
    if pdf:
        info = parse_pdfinfo(run(["pdfinfo", str(pdf)]).stdout)
        pdf_meta = info
        try:
            page_count = int(info.get("Pages", "0"))
        except ValueError:
            page_count = 0
        add_check(checks, "pdf.page_count", page_count == args.expected_pages, f"pages: {page_count}; expected: {args.expected_pages}")
        size_match = re.search(r"([0-9.]+)\s+x\s+([0-9.]+)\s+pts", info.get("Page size", ""))
        a4 = False
        if size_match:
            width, height = map(float, size_match.groups())
            a4 = abs(width - 595) < 3 and abs(height - 842) < 3
        add_check(checks, "pdf.a4", a4, info.get("Page size", "missing page size"))
        add_check(checks, "pdf.unencrypted", info.get("Encrypted", "").casefold() == "no", info.get("Encrypted", "missing"))

        pdf_text = run(["pdftotext", "-layout", str(pdf), "-"]).stdout
        (evidence / "pdf.txt").write_text(pdf_text, encoding="utf-8")
        page_texts = pdf_text.split("\f")
        if page_texts and not page_texts[-1].strip():
            page_texts.pop()

        counts = {label: pdf_text.count(label) for label in ("烦恼", "办法", "解决了什么", "代价是什么")}
        exact_cards = len(set(counts.values())) == 1 and counts["解决了什么"] == 10
        add_check(checks, "pdf.eli5_cards", exact_cards, json.dumps(counts, ensure_ascii=False))
        add_check(
            checks,
            "pdf.main_flow",
            bool(page_texts) and has_all(page_texts[0], ("主线", "角色")),
            "page 1 has main flow and roles",
        )

        pair_pages_ok = len(page_texts) >= 6 and all(
            page_texts[index].count("烦恼") == 2
            and page_texts[index].count("办法") == 2
            and page_texts[index].count("解决了什么") == 2
            and page_texts[index].count("代价是什么") == 2
            for index in range(1, 6)
        )
        add_check(checks, "pdf.two_cards_per_page", pair_pages_ok, "pages 2-6 each contain two complete cards")

        page7 = page_texts[6] if len(page_texts) > 6 else ""
        page8 = page_texts[7] if len(page_texts) > 7 else ""
        page9 = page_texts[8] if len(page_texts) > 8 else ""
        page10 = page_texts[9] if len(page_texts) > 9 else ""
        add_check(
            checks,
            "pdf.framework_io",
            has_any(page7, ("FIGURE", "Figure", "原图", "教学重绘"))
            and has_all(page7, ("输入", "操作", "输出", "下游")),
            "page 7 contains framework provenance and input/operation/output/downstream",
        )
        add_check(
            checks,
            "pdf.training_ledger",
            has_any(page8, ("训练", "WHO UPDATES WHAT"))
            and has_any(page8, ("Loss", "loss", "Reward", "reward", "Objective", "目标")),
            "page 8 contains the training objective ledger",
        )
        add_check(
            checks,
            "pdf.evidence_boundary",
            has_any(page9, ("证据", "EVIDENCE"))
            and has_any(page9, ("边界", "未证明", "没有证明", "未公开", "未披露")),
            "page 9 separates metrics, evidence, and limitations",
        )
        add_check(
            checks,
            "pdf.migration_route",
            has_any(page10, ("迁移", "MINIMUM TEST", "小实验"))
            and has_any(page10, ("学习路线", "一遍过完", "下一站")),
            "page 10 contains a falsifiable migration and learning route",
        )
        bad_dashes = {char: pdf_text.count(char) for char in ("‑", "–", "−") if char in pdf_text}
        add_check(checks, "pdf.ascii_hyphens", not bad_dashes, f"non-ASCII dash counts: {bad_dashes}")

        rendered_pages, contact = render_pdf(pdf, evidence)
        add_check(
            checks,
            "pdf.rendered_pages",
            len(rendered_pages) == page_count and bool(contact and contact.is_file()),
            f"rendered {len(rendered_pages)} pages; contact sheet: {contact}",
        )

    automated_pass = all(check["status"] == "pass" for check in checks)
    report = {
        "schema_version": 1,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "article": article_id,
        "note": str(note),
        "note_sha256": sha256(note),
        "vault_root": str(vault_root),
        "pdf": str(pdf) if pdf else None,
        "pdf_sha256": sha256(pdf) if pdf else None,
        "figure_files": [str(path) for path in figures if path],
        "expected_pages": args.expected_pages,
        "pdf_metadata": pdf_meta,
        "automated_status": "pass" if automated_pass else "fail",
        "visual_status": "pending",
        "overall_status": "pending_visual_review" if automated_pass else "fail",
        "checks": checks,
    }
    (run_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# ONV report",
        "",
        f"- Article: `{article_id}`",
        f"- Note: `{note}`",
        f"- PDF: `{pdf}`",
        f"- Automated status: **{report['automated_status'].upper()}**",
        "- Visual status: **PENDING**",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        box = "x" if check["status"] == "pass" else " "
        lines.append(f"- [{box}] `{check['id']}`: {check['detail']}")
    (run_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    invocation = " ".join(sys.argv)
    (run_dir / "transcript.txt").write_text(
        f"command: {invocation}\nautomated_status: {report['automated_status']}\ncontact_sheet: {contact}\n",
        encoding="utf-8",
    )
    if automated_pass:
        print("AUTOMATED_PASS")
        print(f"VISUAL_REVIEW_REQUIRED: {contact}")
        return 0
    print("ONV_AUTOMATED_FAIL")
    for check in checks:
        if check["status"] == "fail":
            print(f"FAIL {check['id']}: {check['detail']}")
    return 1


def attest(args: argparse.Namespace) -> int:
    run_dir = absolute(args.run_dir)
    report_path = run_dir / "report.json"
    if not report_path.is_file():
        fail(f"report not found: {report_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    contact = run_dir / "evidence/contact-sheet.png"
    if not contact.is_file():
        fail(f"contact sheet not found: {contact}")
    payload = {
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": args.status,
        "reviewer": args.reviewer,
        "comment": args.comment,
        "contact_sheet": str(contact),
        "note_sha256": report.get("note_sha256"),
        "pdf_sha256": report.get("pdf_sha256"),
    }
    (run_dir / "visual-review.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"VISUAL_{args.status.upper()}")
    return 0 if args.status == "pass" else 1


def status(args: argparse.Namespace) -> int:
    run_dir = absolute(args.run_dir)
    report_path = run_dir / "report.json"
    visual_path = run_dir / "visual-review.json"
    if not report_path.is_file():
        fail(f"report not found: {report_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    visual = json.loads(visual_path.read_text(encoding="utf-8")) if visual_path.is_file() else None
    if report.get("automated_status") != "pass":
        print("ONV_FAIL: automated checks failed")
        return 1
    if not visual:
        print("ONV_PENDING: visual review missing")
        return 2
    note = Path(report.get("note", ""))
    pdf_value = report.get("pdf")
    pdf = Path(pdf_value) if pdf_value else None
    if not note.is_file() or sha256(note) != report.get("note_sha256"):
        print("ONV_FAIL: note changed or disappeared after automated verification")
        return 1
    if pdf is None or not pdf.is_file() or sha256(pdf) != report.get("pdf_sha256"):
        print("ONV_FAIL: PDF changed or disappeared after automated verification")
        return 1
    if visual.get("note_sha256") != report.get("note_sha256") or visual.get("pdf_sha256") != report.get("pdf_sha256"):
        print("ONV_FAIL: visual attestation hashes do not match the report")
        return 1
    if visual.get("status") != "pass":
        print("ONV_FAIL: visual review failed")
        return 1
    print("ONV_PASS")
    return 0


def cleanup(args: argparse.Namespace) -> int:
    run_dir = absolute(args.run_dir)
    scratch = run_dir / "scratch"
    if scratch.is_dir():
        shutil.rmtree(scratch)
    print(f"ONV_CLEANUP_OK: evidence preserved at {run_dir}")
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)

    doctor_parser = sub.add_parser("doctor", help="check dependencies and source paths")
    doctor_parser.add_argument("--note", required=True)
    doctor_parser.add_argument("--vault-root", required=True)
    doctor_parser.set_defaults(func=doctor)

    verify_parser = sub.add_parser("verify", help="run structural checks and render evidence")
    verify_parser.add_argument("--note", required=True)
    verify_parser.add_argument("--vault-root", required=True)
    verify_parser.add_argument("--article")
    verify_parser.add_argument("--expected-pages", type=int, default=10)
    verify_parser.add_argument("--run-dir", required=True)
    verify_parser.set_defaults(func=verify)

    attest_parser = sub.add_parser("attest", help="record the contact-sheet visual review")
    attest_parser.add_argument("--run-dir", required=True)
    attest_parser.add_argument("--status", required=True, choices=("pass", "fail"))
    attest_parser.add_argument("--reviewer", required=True)
    attest_parser.add_argument("--comment", required=True)
    attest_parser.set_defaults(func=attest)

    status_parser = sub.add_parser("status", help="combine automated and visual results")
    status_parser.add_argument("--run-dir", required=True)
    status_parser.set_defaults(func=status)

    cleanup_parser = sub.add_parser("cleanup", help="remove run scratch while preserving evidence")
    cleanup_parser.add_argument("--run-dir", required=True)
    cleanup_parser.set_defaults(func=cleanup)
    return root


def main() -> int:
    args = parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
