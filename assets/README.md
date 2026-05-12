# Assets

`architecture.png` is the system diagram embedded at the top of the project README.
`architecture.py` is the matplotlib script that produced it; the diagram is fully reproducible.

## What the diagram shows

```
  Conversation history  (EN / FR / Franglais, 1 to 28 turns)
            |
            v
  mmBERT classifier  (fine-tuned jhu-clsp/mmBERT-base, ~20 ms GPU)
            |
            |  risk score in [0, 1]
            |  injected into prompt as primer
            v
  Cohere c4ai LLM judge  (~900 ms per call)
    Chain-of-thought reasoning:
      1. Opening intent
      2. Escalation
      3. Crisis signals
      4. Vulnerability
      5. Trajectory                                  on error
    Output: JSON (reasoning + label + confidence)  - - - - - >  Fail-safe
            |                                                   defaults to
            |  confidence in [0, 1]                              high_risk
            v
        <  >=  0.45 ?  >
       /              \
     yes               no
     /                  \
  high_risk          low_risk
     |                  |
     v                  v
  Flag returned to VA layer
  KHP counsellor decides final escalation
```

## Design choices

- Light tinted cards with strong same-color borders for each semantic category (input, model, decision, outcomes, human, side annotation), instead of heavy solid fills.
- Drop shadows for depth without weight.
- One restrained palette per role: blue for input, violet for model components, amber for the decision, red and green for outcomes, slate for the human handoff, dashed gray for the fail-safe side note.
- Real diamond shape for the decision node.
- Straight vertical drops for the outcome-to-handoff arrows (no awkward elbows).
- Transparent canvas so the diagram reads on both light and dark GitHub themes.

## Regenerating

```bash
python3 assets/architecture.py
```

Requires `matplotlib`. Output is written in place to `assets/architecture.png`. Canvas is 16.5 by 13 matplotlib units; the saved PNG is approximately 2800 by 2200 px at 170 dpi with a transparent background.
