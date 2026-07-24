# Codex Tier Display Widget

A compact, frameless, always-on-top desktop widget that ranks every public Codex model tier and shows the top three by short model name, IQ, and USD cost.

## Highlights

- Shows only the model name, IQ, and cost.
- Drag any row to move the widget; press Escape to close it.
- Fetches public benchmark data on launch and every 10 minutes afterwards.
- Recalculates every public model tier every 10 minutes, applies an IQ 80 eligibility gate, and ranks eligible tiers by `IQ / cost`.
- Never reads or changes Codex configuration, switches models, or controls Codex.

## Run

Requires Windows 10/11 and Python 3.11+.

```powershell
python scripts/launch_widget.py
```

Edit `src/codex_tier_widget/config.py` to change the IQ threshold or display count. See the [Chinese README](README.md) for full documentation.
