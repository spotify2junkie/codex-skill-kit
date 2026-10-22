import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import badminton_review as review  # noqa: E402


def make_plan(source: Path) -> dict:
    categories = [
        "core_technique",
        "improvable_rally",
        "highlight_point",
        "core_technique",
    ]
    segments = []
    for index, category in enumerate(categories):
        start = index * 12.0
        segments.append(
            {
                "id": f"rally-{index + 1}",
                "category": category,
                "start_s": start,
                "serve_contact_s": start + 1.0,
                "dead_ball_s": start + 9.0,
                "end_s": start + 10.0,
                "verdict": "good" if index % 2 == 0 else "bad",
                "reason": "The visible movement supports this conclusion.",
                "drill": "Repeat the movement with a controlled split step.",
                "subtitle": "接发准备及时",
                "experts": {
                    "technique": {
                        "at_s": start + 3.0,
                        "conclusion": "The racket preparation is visible.",
                    },
                    "footwork_position": {
                        "at_s": start + 5.0,
                        "conclusion": "The recovery position is visible.",
                    },
                    "tactics_shot_selection": {
                        "at_s": start + 7.0,
                        "conclusion": "The shot direction is visible.",
                    },
                },
            }
        )
    return {
        "schema_version": 1,
        "source_path": str(source),
        "source_duration_s": 480.0,
        "focus": "Near-side player identified by shirt color only.",
        "reference_comparison": (
            "Documented workflow comparison; reference runtime was "
            "not executed."
        ),
        "segments": segments,
    }


class ValidatePlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = Path.home() / "ops/tmp/badminton-cut/sample.MOV"
        self.media = {
            "duration_s": 480.0,
            "width": 3840,
            "height": 2160,
            "has_audio": True,
        }
        self.plan = make_plan(self.source)

    def test_accepts_complete_categories_and_three_timestamped_experts(
        self,
    ) -> None:
        result = review.validate_plan(self.plan, self.source, self.media)
        self.assertEqual(len(result), 4)
        self.assertEqual(
            {s["category"] for s in result}, review.REQUIRED_CATEGORIES
        )

    def test_rejects_missing_category(self) -> None:
        for segment in self.plan["segments"]:
            segment["category"] = "core_technique"
        with self.assertRaisesRegex(
            review.ReviewError, "Missing required categories"
        ):
            review.validate_plan(self.plan, self.source, self.media)

    def test_rejects_short_pre_serve_margin(self) -> None:
        self.plan["segments"][0]["start_s"] = 0.7
        self.plan["segments"][0]["serve_contact_s"] = 1.0
        with self.assertRaisesRegex(
            review.ReviewError, "planned rally padding"
        ):
            review.validate_plan(self.plan, self.source, self.media)

    def test_rejects_runtime_over_the_stricter_limit(self) -> None:
        for index, segment in enumerate(self.plan["segments"]):
            segment["start_s"] = index * 31.0
            segment["serve_contact_s"] = segment["start_s"] + 1.0
            segment["dead_ball_s"] = segment["start_s"] + 30.0
            segment["end_s"] = segment["start_s"] + 31.0
            segment["experts"]["technique"]["at_s"] = segment["start_s"] + 3.0
            segment["experts"]["footwork_position"]["at_s"] = (
                segment["start_s"] + 5.0
            )
            segment["experts"]["tactics_shot_selection"]["at_s"] = (
                segment["start_s"] + 7.0
            )
        with self.assertRaisesRegex(review.ReviewError, "Planned runtime"):
            review.validate_plan(self.plan, self.source, self.media)

    def test_rejects_overlapping_rallies(self) -> None:
        self.plan["segments"][1]["start_s"] = 9.0
        self.plan["segments"][1]["serve_contact_s"] = 10.0
        self.plan["segments"][1]["dead_ball_s"] = 17.0
        self.plan["segments"][1]["end_s"] = 18.0
        with self.assertRaisesRegex(review.ReviewError, "must not overlap"):
            review.validate_plan(self.plan, self.source, self.media)

    def test_rejects_missing_independent_expert(self) -> None:
        del self.plan["segments"][0]["experts"]["tactics_shot_selection"]
        with self.assertRaisesRegex(
            review.ReviewError, "exactly three independent"
        ):
            review.validate_plan(self.plan, self.source, self.media)


class BoundaryAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = Path.home() / "ops/tmp/badminton-cut/IMG_8674.MOV"
        self.media = {
            "duration_s": 480.0,
            "width": 3840,
            "height": 2160,
            "has_audio": True,
        }
        self.plan = make_plan(self.source)
        self.segments = review.validate_plan(
            self.plan, self.source, self.media
        )
        self.manifest_path = Path("reviewed-boundaries.json")
        self.rows = []
        for segment in self.segments:
            for event, field in (
                ("serve", "serve_contact_s"),
                ("dead_ball", "dead_ball_s"),
            ):
                self.rows.append(
                    {
                        "source": str(self.source.resolve()),
                        "segment": segment["id"],
                        "event": event,
                        "timestamp_s": segment[field],
                        "image": "/tmp/reviewed.jpg",
                        "exit_code": 0,
                        "sample_rate_fps": 8,
                        "window_duration_s": 1.0,
                        "visual_review": "PASS",
                    }
                )

    def validate_rows(self) -> Path:
        with (
            patch.object(Path, "is_file", return_value=True),
            patch.object(
                Path, "read_text", return_value=json.dumps(self.rows)
            ),
        ):
            return review.validate_boundary_audit(
                self.segments, self.source, self.manifest_path
            )

    def test_accepts_approved_evidence_for_each_boundary(self) -> None:
        result = self.validate_rows()

        self.assertEqual(result, self.manifest_path.resolve())

    def test_rejects_a_stale_serve_timestamp(self) -> None:
        self.rows[0]["timestamp_s"] = 75.2

        with self.assertRaisesRegex(review.ReviewError, "Stale boundary"):
            self.validate_rows()

    def test_rejects_a_boundary_without_visual_approval(self) -> None:
        self.rows[0]["visual_review"] = "PENDING"

        with self.assertRaisesRegex(
            review.ReviewError, "not visually approved"
        ):
            self.validate_rows()


if __name__ == "__main__":
    unittest.main()
