#!/usr/bin/env python3
"""Regression tests for verify_note_bundle.py (stdlib only)."""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).with_name("verify_note_bundle.py")
SPEC = importlib.util.spec_from_file_location("verify_note_bundle", SCRIPT)
assert SPEC and SPEC.loader
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


class VerifyNoteBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.vault = self.root / "vault"
        self.vault.mkdir()
        self.note = self.root / "note.md"
        self.pdf = self.root / "paper.pdf"
        self.pdf.write_bytes(b"fake pdf one")
        self.source = self.root / "source.txt"
        self.source.write_text("source", encoding="utf-8")
        self.renderer = self.root / "renderer.js"
        self.renderer.write_text("render", encoding="utf-8")
        self.source_report = self.root / "source-report.txt"
        self.source_report.write_text("source review PASS", encoding="utf-8")
        self.visual_report = self.root / "visual-report.txt"
        self.visual_report.write_text("visual review PASS", encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    @staticmethod
    def digest(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def invoke(self, *extra: str, pages: int = 2, text: str = "解决了什么\n代价是什么") -> tuple[int, dict]:
        output = io.StringIO()
        with mock.patch.object(verifier, "inspect_pdf", return_value=([], pages, text)):
            with contextlib.redirect_stdout(output):
                code = verifier.main(
                    [
                        "--note",
                        str(self.note),
                        "--vault-root",
                        str(self.vault),
                        *extra,
                    ]
                )
        return code, json.loads(output.getvalue())

    def write_one_article_note(self, *, title: str = "Paper one", pdf: str = "paper.pdf") -> None:
        self.note.write_text(
            f"## 01. {title}\n\nSource: https://example.test/paper-one\n\n![[{pdf}]]\n",
            encoding="utf-8",
        )

    def manifest_one(self, *, source_figure: dict | None = None) -> Path:
        inputs = {
            "source.txt": self.digest(self.source),
            "renderer.js": self.digest(self.renderer),
        }
        if source_figure is not None:
            inputs[source_figure["path"]] = source_figure["sha256"]
        pdf_hash = self.digest(self.pdf)
        reviews = [
            {
                "lane": "source",
                "reviewer": "source-reviewer",
                "status": "PASS",
                "pdf_sha256": pdf_hash,
                "inputs": inputs,
                "evidence": "source-report.txt",
                "evidence_sha256": self.digest(self.source_report),
            },
            {
                "lane": "visual",
                "reviewer": "visual-reviewer",
                "status": "PASS",
                "pdf_sha256": pdf_hash,
                "inputs": inputs,
                "evidence": "visual-report.txt",
                "evidence_sha256": self.digest(self.visual_report),
                "pages_checked": [1, 2],
            },
        ]
        if source_figure is not None:
            reviews[1]["source_figure_page"] = source_figure["pdf_page"]
        manifest = self.root / "bundle.json"
        manifest.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "articles": [
                        {
                            "source_id": "paper-one",
                            "rank": "01",
                            "title": "Paper one",
                            "canonical_url": "https://example.test/paper-one",
                            "pdf": "paper.pdf",
                            "pdf_sha256": pdf_hash,
                            "inputs": inputs,
                            "cards": 1,
                            **({"source_figure": source_figure} if source_figure is not None else {}),
                            "reviews": reviews,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        return manifest

    def strict_invoke(self, manifest: Path, *extra: str) -> tuple[int, dict]:
        return self.invoke("--manifest", str(manifest), *extra)

    def test_manifest_valid_and_exact_mapping(self) -> None:
        self.write_one_article_note()
        manifest = self.manifest_one()
        code, report = self.strict_invoke(manifest, "--expected-articles", "1", "--expected-pdfs", "1")
        self.assertEqual(code, 0, report)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["verification_level"], "manifest_consistency")

    def test_empty_note_cannot_pass_expected_counts(self) -> None:
        self.note.write_text("", encoding="utf-8")
        code, report = self.invoke("--expected-articles", "1", "--expected-pdfs", "1")
        self.assertNotEqual(code, 0)
        self.assertTrue(report["errors"])

    def test_canonical_url_prefix_is_not_exact_match(self) -> None:
        self.write_one_article_note()
        self.note.write_text(
            "## 01. Paper one\nSource: https://example.test/paper-one-wrong\n![[paper.pdf]]\n",
            encoding="utf-8",
        )
        manifest = self.manifest_one()
        code, report = self.strict_invoke(manifest)
        self.assertNotEqual(code, 0)
        self.assertTrue(any("canonical_url" in error for error in report["errors"]))

    def test_blank_note_without_count_flags_is_not_pass(self) -> None:
        self.note.write_text("  \n", encoding="utf-8")
        code, report = self.invoke()
        self.assertNotEqual(code, 0)
        self.assertIn("note is empty or whitespace-only", report["errors"])

    def test_empty_pdf_text_cannot_verify_takeaway_labels(self) -> None:
        self.write_one_article_note()
        code, report = self.invoke(text="")
        self.assertNotEqual(code, 0)
        self.assertTrue(any("nonzero" in error for error in report["errors"]))

    def test_explicit_twelve_pages_overrides_implicit_ten_maximum(self) -> None:
        self.write_one_article_note()
        code, report = self.invoke("--expected-pdf-pages", "12", pages=12)
        self.assertEqual(code, 0, report)

    def test_swapped_pdf_is_rejected(self) -> None:
        second = self.root / "paper-two.pdf"
        second.write_bytes(b"fake pdf two")
        self.note.write_text(
            "## 01. Paper one\nhttps://example.test/paper-one\n![[paper.pdf]]\n\n"
            "## 02. Paper two\nhttps://example.test/paper-two\n![[paper-two.pdf]]\n",
            encoding="utf-8",
        )
        # Keep the fixture compact while changing only the manifest-to-section mapping.
        first = json.loads(self.manifest_one().read_text(encoding="utf-8"))["articles"][0]
        first["pdf"] = "paper-two.pdf"
        first["pdf_sha256"] = self.digest(second)
        first["canonical_url"] = "https://example.test/paper-one"
        second_article = dict(first, source_id="paper-two", rank="02", title="Paper two", pdf="paper.pdf", pdf_sha256=self.digest(self.pdf), canonical_url="https://example.test/paper-two")
        manifest = self.root / "swapped.json"
        manifest.write_text(json.dumps({"schema_version": 1, "articles": [first, second_article]}), encoding="utf-8")
        code, report = self.strict_invoke(manifest)
        self.assertNotEqual(code, 0)
        self.assertTrue(any("embedded" in error or "reused" in error for error in report["errors"]))

    def test_current_input_mutation_invalidates_manifest(self) -> None:
        self.write_one_article_note()
        manifest = self.manifest_one()
        self.source.write_text("changed", encoding="utf-8")
        code, report = self.strict_invoke(manifest)
        self.assertNotEqual(code, 0)
        self.assertTrue(any("input hash mismatch" in error for error in report["errors"]))

    def test_stale_review_hash_is_rejected(self) -> None:
        self.write_one_article_note()
        manifest = self.manifest_one()
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["articles"][0]["reviews"][0]["pdf_sha256"] = "0" * 64
        manifest.write_text(json.dumps(data), encoding="utf-8")
        code, report = self.strict_invoke(manifest)
        self.assertNotEqual(code, 0)
        self.assertTrue(any("does not match article PDF hash" in error for error in report["errors"]))

    def test_issues_review_status_is_not_acceptance(self) -> None:
        self.write_one_article_note()
        manifest = self.manifest_one()
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["articles"][0]["reviews"][0]["status"] = "ISSUES"
        manifest.write_text(json.dumps(data), encoding="utf-8")
        code, report = self.strict_invoke(manifest)
        self.assertNotEqual(code, 0)
        self.assertTrue(any("status must be PASS" in error for error in report["errors"]))

    def test_missing_report_is_rejected(self) -> None:
        self.write_one_article_note()
        manifest = self.manifest_one()
        self.source_report.unlink()
        code, report = self.strict_invoke(manifest)
        self.assertNotEqual(code, 0)
        self.assertTrue(any("missing evidence report" in error for error in report["errors"]))

    def test_incomplete_visual_pages_are_rejected(self) -> None:
        self.write_one_article_note()
        manifest = self.manifest_one()
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["articles"][0]["reviews"][1]["pages_checked"] = [1]
        manifest.write_text(json.dumps(data), encoding="utf-8")
        code, report = self.strict_invoke(manifest)
        self.assertNotEqual(code, 0)
        self.assertTrue(any("every actual page" in error for error in report["errors"]))

    def test_original_figure_missing_or_page_wrong_is_rejected(self) -> None:
        self.write_one_article_note()
        figure = self.root / "figure.svg"
        figure.write_text("<svg/>", encoding="utf-8")
        source_figure = {"path": "figure.svg", "sha256": self.digest(figure), "pdf_page": 3}
        manifest = self.manifest_one(source_figure=source_figure)
        code, report = self.strict_invoke(manifest)
        self.assertNotEqual(code, 0)
        self.assertTrue(any("outside the PDF page range" in error for error in report["errors"]))
        figure.unlink()
        code, report = self.strict_invoke(manifest)
        self.assertNotEqual(code, 0)
        self.assertTrue(any("missing file" in error for error in report["errors"]))

    def test_malformed_manifest_and_requested_report_are_json_fail(self) -> None:
        self.write_one_article_note()
        manifest = self.root / "bad.json"
        manifest.write_text("{not-json", encoding="utf-8")
        report_path = self.root / "qa" / "report.json"
        code, report = self.strict_invoke(manifest, "--json-report", str(report_path))
        self.assertNotEqual(code, 0)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["status"], "FAIL")

    def test_basic_maximum_allows_nine_and_rejects_eleven(self) -> None:
        self.write_one_article_note()
        code, report = self.invoke(pages=9)
        self.assertEqual(code, 0, report)
        code, report = self.invoke(pages=11)
        self.assertNotEqual(code, 0)
        self.assertTrue(any("maximum=10" in error for error in report["errors"]))

    def test_bad_manifest_paths_return_json_fail(self) -> None:
        self.write_one_article_note()
        for bad_path in ("~reading-radar-user-that-does-not-exist/file", "bad\x00file"):
            with self.subTest(path=repr(bad_path)):
                manifest = self.manifest_one()
                data = json.loads(manifest.read_text(encoding="utf-8"))
                data["articles"][0]["inputs"] = {bad_path: "0" * 64}
                manifest.write_text(json.dumps(data), encoding="utf-8")
                report_path = self.root / "path-failure.json"
                code, report = self.strict_invoke(manifest, "--json-report", str(report_path))
                self.assertNotEqual(code, 0)
                self.assertEqual(report["status"], "FAIL")
                self.assertEqual(json.loads(report_path.read_text())["status"], "FAIL")

    def test_bad_cli_path_returns_json_fail(self) -> None:
        code, report = self.invoke("--note", "~reading-radar-user-that-does-not-exist/note.md")
        self.assertNotEqual(code, 0)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("invalid note path" in error for error in report["errors"]))

    def test_explicit_exact_ten_rejects_nine(self) -> None:
        self.write_one_article_note()
        code, report = self.invoke("--expected-pdf-pages", "10", pages=9)
        self.assertNotEqual(code, 0)
        self.assertTrue(any("expected=10" in error for error in report["errors"]))

    def test_literal_api_template_is_allowed(self) -> None:
        self.note.write_text("literal {{$userId}}\n![[paper.pdf]]\n", encoding="utf-8")
        code, report = self.invoke(pages=2)
        self.assertEqual(code, 0, report)

    def test_documented_todo_word_is_not_a_scaffold(self) -> None:
        self.write_one_article_note()
        self.note.write_text(self.note.read_text() + "\nThe API exposes a TODO state.\n", encoding="utf-8")
        code, report = self.invoke()
        self.assertEqual(code, 0, report)
        self.note.write_text(self.note.read_text() + "\n[TODO: add source evidence]\n", encoding="utf-8")
        code, report = self.invoke()
        self.assertNotEqual(code, 0)
        self.assertTrue(any("TODO marker" in error for error in report["errors"]))

    def test_old_basic_exact_pages_and_cards_invocation(self) -> None:
        self.write_one_article_note()
        code, report = self.invoke(
            "--expected-pdf-pages",
            "2",
            "--expected-cards",
            "1",
            pages=2,
        )
        self.assertEqual(code, 0, report)


if __name__ == "__main__":
    unittest.main()
