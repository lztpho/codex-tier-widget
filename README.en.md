# Codex Tier Display Widget

A compact, frameless, always-on-top desktop widget for comparing three Codex model tiers by short model name, IQ, and USD cost.

## Highlights

- Shows only the model name, IQ, and cost.
- Drag any row to move the widget; press Escape to close it.
- Fetches public benchmark data on launch and every 10 minutes afterwards.
- Uses an IQ 80 eligibility gate, then ranks eligible tiers by `IQ / cost`.
- Never reads or changes Codex configuration, switches models, or controls Codex.

## Run

Requires Windows 10/11 and Python 3.11+.

```powershell
python scripts/launch_widget.py
```

Edit `src/codex_tier_widget/config.py` to change the three display tiers or the IQ threshold. See the [Chinese README](README.md) for full documentation.
