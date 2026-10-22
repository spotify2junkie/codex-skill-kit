from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import audit_rally_boundaries as audit  # noqa: E402


class BoundaryEventsTests(unittest.TestCase):
    def test_creates_serve_and_dead_ball_windows_for_each_rally(self) -> None:
        plan = {
            "segments": [
                {
                    "id": "rally-01",
                    "serve_contact_s": 12.25,
                    "dead_ball_s": 18.5,
                },
                {
                    "id": "rally-02",
                    "serve_contact_s": 42.0,
                    "dead_ball_s": 49.75,
                },
            ]
        }

        events = audit.boundary_events(plan)

        self.assertEqual(len(events), 4)
        self.assertEqual(
            [(event["segment"], event["event"]) for event in events],
            [
                ("rally-01", "serve"),
                ("rally-01", "dead_ball"),
                ("rally-02", "serve"),
                ("rally-02", "dead_ball"),
            ],
        )
        self.assertEqual(events[0]["window_start_s"], 11.5)
        self.assertEqual(events[1]["window_start_s"], 17.75)
        self.assertEqual(events[2]["window_start_s"], 41.25)
        self.assertEqual(events[3]["window_start_s"], 49.0)

    def test_clamps_initial_window_to_start_of_source(self) -> None:
        plan = {
            "segments": [
                {
                    "id": "rally-01",
                    "serve_contact_s": 0.4,
                    "dead_ball_s": 2.0,
                }
            ]
        }

        events = audit.boundary_events(plan)

        self.assertEqual(events[0]["window_start_s"], 0.0)


if __name__ == "__main__":
    unittest.main()
