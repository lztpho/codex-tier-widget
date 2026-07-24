# Codex Tier Display Widget

## Why does this project exist?

When using Codex for coding, model names, reasoning efforts, IQ scores, and prices are not always easy to compare in one place. Stronger models are usually more expensive, while the cheapest option may not be capable enough for a difficult task.

This project provides a small desktop widget that reads public benchmark data from Codex Radar and surfaces the three most cost-effective model tiers that meet the minimum IQ requirement. It solves a simple problem: quickly finding a capable and affordable model without repeatedly opening a web page or calculating the trade-off by hand.

## Preview

![Codex tier widget screenshot](assets/widget-screenshot.png)

The values in the preview are example public data; the widget refreshes its values from the data source.

## What it does

- Shows only a short model name, IQ, and average cost.
- Recalculates every public model tier on launch and every 10 minutes.
- Prioritizes IQ ≥ 80, then ranks by `IQ / average_price_usd`.
- Shows the top three results and uses local cache data when the network is unavailable.
- Lets you drag any row; press Escape to hide the widget. Use the system tray menu to show, hide, refresh, or exit.

## What it does not do

The widget is read-only. It never reads or modifies Codex configuration, switches models, restarts Codex, or uploads code and prompts.

## Run

Requires Windows 10/11 and Python 3.11+:

```powershell
python -m pip install -r requirements.txt
python scripts/launch_widget.py
```

Closing or pressing Escape hides the widget but keeps the process running. Use the system tray menu to exit completely.

See the [Chinese README](README.md) for the full documentation.
