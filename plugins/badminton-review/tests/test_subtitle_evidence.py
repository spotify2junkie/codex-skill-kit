import json
from importlib import import_module
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from typing import Any
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
evidence = import_module("subtitle_evidence")
EvidenceError = evidence.EvidenceError
sample_timestamps = evidence.sample_timestamps
validate_evidence = evidence.validate_evidence


class SampleTimestampTests(unittest.TestCase):
    def test_samples_each_four_second_point_before_duration(self) -> None:
        timestamps = sample_timestamps(49.803, 4.0)

        expected = [float(value) for value in range(0, 49, 4)]
        self.assertEqual(timestamps, expected)
        self.assertEqual(len(timestamps), 13)

    def test_includes_a_point_below_the_supplied_duration(self) -> None:
        timestamps = sample_timestamps(52.006, 4.0)

        self.assertEqual(timestamps[-1], 52.0)
        self.assertEqual(len(timestamps), 14)

    def test_old_stream_durations_yield_15_13_and_13_samples(self) -> None:
        counts = [
            len(sample_timestamps(duration, 4.0))
            for duration in (56.993355, 51.981676, 49.788405)
        ]

        self.assertEqual(counts, [15, 13, 13])

    def test_does_not_sample_at_the_duration_boundary(self) -> None:
        self.assertEqual(sample_timestamps(52.0, 4.0)[-1], 48.0)

    def test_rejects_non_positive_duration_or_interval(self) -> None:
        with self.assertRaisesRegex(EvidenceError, "duration"):
            sample_timestamps(0.0, 4.0)
        with self.assertRaisesRegex(EvidenceError, "interval"):
            sample_timestamps(10.0, 0.0)


class EvidenceValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.before = self.root / "before.mp4"
        self.after = self.root / "after.mp4"
        self.before.touch()
        self.after.touch()
        self.manifest_path = self.root / "manifest.json"
        self.samples: list[dict[str, Any]] = []
        for index, timestamp in enumerate(sample_timestamps(8.1, 4.0)):
            row = {
                "timestamp_s": timestamp,
                "exit_code": 0,
                "visual_review": "PASS",
            }
            for kind in ("before_image", "after_image", "comparison_image"):
                image_path = self.root / f"{kind}-{index}.jpg"
                image_path.touch()
                row[kind] = str(image_path)
            self.samples.append(row)
        self.after_contacts: list[Path] = [
            self.root / "after-contact-01.jpg"
        ]
        self.comparison_contacts: list[Path] = [
            self.root / "comparison-contact-01.jpg"
        ]
        for image_path in self.after_contacts + self.comparison_contacts:
            image_path.touch()
        self.manifest: dict[str, Any] = {
            "schema_version": 1,
            "before_video": str(self.before),
            "after_video": str(self.after),
            "before_duration_s": 10.0,
            "after_video_duration_s": 8.1,
            "interval_s": 4.0,
            "sample_width_px": 2560,
            "sample_height_px": 1440,
            "after_contact_sheets": [
                str(path) for path in self.after_contacts
            ],
            "comparison_contact_sheets": [
                str(path) for path in self.comparison_contacts
            ],
            "samples": self.samples,
        }
        self.write_manifest()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_manifest(self) -> None:
        self.manifest_path.write_text(
            json.dumps(self.manifest), encoding="utf-8"
        )

    def validate(self) -> dict[str, Any]:
        return validate_evidence(
            self.manifest_path,
            self.after,
            duration_s=8.1,
            width_px=2560,
            height_px=1440,
        )

    def test_accepts_complete_passed_frame_evidence(self) -> None:
        manifest = self.validate()

        self.assertEqual(len(manifest["samples"]), 3)

    def test_rejects_a_missing_sample(self) -> None:
        self.manifest["samples"].pop()
        self.write_manifest()

        with self.assertRaisesRegex(EvidenceError, "incomplete"):
            self.validate()

    def test_rejects_an_unreviewed_sample(self) -> None:
        self.manifest["samples"][0]["visual_review"] = "PENDING"
        self.write_manifest()

        with self.assertRaisesRegex(EvidenceError, "not passed"):
            self.validate()

    def test_rejects_a_missing_comparison_image(self) -> None:
        self.manifest["samples"][0]["comparison_image"] = str(
            self.root / "missing.jpg"
        )
        self.write_manifest()

        with self.assertRaisesRegex(EvidenceError, "image is missing"):
            self.validate()

    def test_rejects_another_after_video(self) -> None:
        other_after = self.root / "other.mp4"
        other_after.touch()

        with self.assertRaisesRegex(EvidenceError, "different after video"):
            validate_evidence(
                self.manifest_path,
                other_after,
                duration_s=8.1,
                width_px=2560,
                height_px=1440,
            )


if __name__ == "__main__":
    unittest.main()
