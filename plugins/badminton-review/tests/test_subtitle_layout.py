import math
from importlib import import_module
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
review = import_module("badminton_review")
layout = import_module("subtitle_layout")
FrameSize = layout.FrameSize
plan_caption = layout.plan_caption


class SubtitleLayoutTests(unittest.TestCase):
    def test_1080p_and_1440p_sizes_clear_the_requested_font_size(self) -> None:
        plan_1080 = plan_caption(
            "字幕", duration_s=10.0, frame=FrameSize(1920, 1080)
        )
        plan_1440 = plan_caption(
            "字幕", duration_s=10.0, frame=FrameSize(2560, 1440)
        )

        self.assertEqual(plan_1080.style.font_size_px, 76)
        self.assertGreaterEqual(plan_1080.style.font_size_px, 56)
        self.assertEqual(plan_1440.style.font_size_px, 101)
        self.assertGreaterEqual(plan_1440.style.font_size_px, 75)
        self.assertGreaterEqual(plan_1080.style.outline_px, 3)
        self.assertGreaterEqual(plan_1440.style.outline_px, 3)

    def test_caption_stays_centered_and_keeps_the_bottom_margin(self) -> None:
        for frame in (FrameSize(1920, 1080), FrameSize(2560, 1440)):
            plan = plan_caption("羽毛球字幕" * 7, duration_s=10.0, frame=frame)
            style = plan.style
            text_height = style.font_size_px * 1.25 * 2
            box_height = (
                text_height + 2 * style.box_padding_px + 2 * style.outline_px
            )
            bottom_margin = (
                frame.height_px * (1 - style.center_y_fraction)
                - box_height / 2
            )

            self.assertEqual(style.center_x_fraction, 0.5)
            self.assertGreaterEqual(style.center_y_fraction, 0.82)
            self.assertLessEqual(style.center_y_fraction, 0.90)
            self.assertGreaterEqual(bottom_margin, frame.height_px * 0.05)

    def test_line_limits_and_pagination_do_not_shrink(self) -> None:
        one_line = plan_caption(
            "甲" * 18, duration_s=8.0, frame=FrameSize(2560, 1440)
        )
        one_page = plan_caption(
            "甲" * 19, duration_s=8.0, frame=FrameSize(2560, 1440)
        )
        max_page = plan_caption(
            "甲" * 36, duration_s=8.0, frame=FrameSize(2560, 1440)
        )
        two_pages = plan_caption(
            "甲" * 37, duration_s=8.0, frame=FrameSize(2560, 1440)
        )
        max_text = plan_caption(
            "甲" * 48, duration_s=8.0, frame=FrameSize(2560, 1440)
        )

        self.assertEqual(
            [len(line) for line in one_line.pages[0].lines], [18]
        )
        self.assertEqual(
            [len(line) for line in one_page.pages[0].lines], [18, 1]
        )
        self.assertEqual(
            [len(line) for line in max_page.pages[0].lines], [18, 18]
        )
        self.assertEqual(len(two_pages.pages), 2)
        self.assertEqual(len(max_text.pages), 2)
        self.assertTrue(
            all(len(page.lines) <= 2 for page in max_text.pages)
        )
        self.assertEqual(len(two_pages.pages[0].lines), 2)
        self.assertTrue(
            all(
                1 <= len(line) <= 18
                for page in two_pages.pages
                for line in page.lines
            )
        )
        self.assertEqual(
            two_pages.style.font_size_px,
            plan_caption(
                "甲", duration_s=8.0, frame=FrameSize(2560, 1440)
            ).style.font_size_px,
        )

    def test_pages_cover_the_clip_contiguously(self) -> None:
        plan = plan_caption(
            "字幕" * 19, duration_s=9.6, frame=FrameSize(2560, 1440)
        )

        self.assertEqual(len(plan.pages), 2)
        self.assertEqual(plan.pages[0].start_s, 0.0)
        self.assertAlmostEqual(plan.pages[-1].end_s, 9.6)
        for previous, current in zip(plan.pages, plan.pages[1:]):
            self.assertEqual(previous.end_s, current.start_s)
        self.assertTrue(
            all(page.end_s > page.start_s for page in plan.pages)
        )

    def test_build_filter_creates_timed_centered_drawtext_pages(self) -> None:
        segments = [
            {
                "id": "rally-1",
                "subtitle": "甲" * 37,
                "start_s": 1.0,
                "end_s": 9.0,
                "source_frame_duration_s": 8.0,
            }
        ]

        graph = review.build_filter(segments, has_audio=False)

        self.assertEqual(graph.count("drawtext="), 2)
        self.assertIn("fontsize=101:borderw=5:bordercolor=black", graph)
        self.assertIn("box=1:boxcolor=black@0.58:boxborderw=18", graph)
        self.assertIn("text_align=center:line_spacing=0", graph)
        self.assertIn("\n", graph)
        self.assertIn("y=h*0.840000-text_h/2", graph)
        self.assertIn("enable='gte(t,0.000000)*lt(t,4.000000)'", graph)
        self.assertIn("enable='gte(t,4.000000)*lt(t,8.000000)'", graph)

    def test_rejects_invalid_duration_and_frame_size(self) -> None:
        with self.assertRaisesRegex(ValueError, "duration"):
            plan_caption(
                "字幕", duration_s=math.inf, frame=FrameSize(2560, 1440)
            )
        with self.assertRaisesRegex(ValueError, "dimensions"):
            plan_caption("字幕", duration_s=2.0, frame=FrameSize(0, 1440))


if __name__ == "__main__":
    unittest.main()
