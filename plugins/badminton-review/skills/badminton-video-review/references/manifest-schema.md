# Review plan schema

The plan is reviewed input to the renderer. All event and clip times are seconds from the source's start. The renderer validates this document before invoking FFmpeg.

```json
{
  "schema_version": 1,
  "source_path": "$HOME/ops/tmp/badminton-cut/IMG_8675.MOV",
  "source_duration_s": 487.073333,
  "focus": "Near-side player in a pink top; identity not inferred",
  "reference_comparison": "Describe the observed output differences and state whether the reference runtime was executed.",
  "segments": [
    {
      "id": "rally-01",
      "category": "core_technique",
      "start_s": 71.0,
      "serve_contact_s": 71.9,
      "dead_ball_s": 78.0,
      "end_s": 78.8,
      "verdict": "good",
      "reason": "Visible evidence for the judgment.",
      "drill": "A short, specific practice drill.",
      "subtitle": "接发准备及时，先做分腿垫步",
      "experts": {
        "technique": {"at_s": 74.2, "conclusion": "Observed technique and its visible evidence."},
        "footwork_position": {"at_s": 75.1, "conclusion": "Observed movement/position and its visible evidence."},
        "tactics_shot_selection": {"at_s": 76.4, "conclusion": "Observed shot choice and its visible evidence."}
      }
    }
  ]
}
```

Allowed categories: `core_technique`, `improvable_rally`, `highlight_point`. Allowed verdicts: `good`, `bad`. Every rally has one timestamped finding for each expert. Keep each sentence tied to an observable event; do not infer intent or identity.
