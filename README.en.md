# Codex Tier Widget

> A persistent floating widget on the right-bottom corner of your Windows desktop, showing Codex tier IQ + price + cost-effectiveness heat-mapped in real time. Click a button to switch Codex's current tier.

[中文 README →](README.md)

## What is this

If you write code with OpenAI Codex, every task you wonder "which model tier should I use for this one?" — this tool is built exactly for that scenario:

- **Persistent desktop widget**: small floating window on the right-bottom, frameless + semi-transparent + always-on-top, never steals screen real estate
- **Real-time data**: pulls [codexradar.com](https://codexradar.com/) IQ benchmarks every 10 minutes
- **One tier, one click**: 3 hand-picked recommended tiers (Light / Medium / Heavy) tuned for "IQ / price" cost-effectiveness
- **Real handoff**: clicking a button writes to `~/.codex/config.toml` directly (Codex restart required to take effect)
- **Color-coded**: greener = better cost-effectiveness, redder = worse — at a glance, you know if you picked a bad tier
- **Zero external dependencies**: pure Python 3.11+ standard library, the whole project is < 30KB

## Screenshot placeholder

```
┌──────────────────────────────────┐
│ Codex Tier · 21:34   ● Live       │ ← status row
│ ──────────────────────────────── │
│ 🟢 Light                        │
│   luna xhigh        IQ 84.4      │
│   $1.63 / run    [ Use this ]    │
│ ──────────────────────────────── │
│ 🟡 Medium                       │
│   terra xhigh       IQ 89.7      │
│   $2.36 / run    [ Use this ]    │
│ ──────────────────────────────── │
│ 🟠 Heavy                        │
│   sol medium        IQ 93.8      │
│   $3.69 / run    [ Use this ]    │
│ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │
│ ⚙️ Current Tier (your Codex)     │
│   gpt-5-codex high  IQ 87.1      │
│   $5.87 / run                    │
│ ──────────────────────────────── │
│ ↻ Refresh · Selected: ●Light      │
└──────────────────────────────────┘
```

> Real screenshot: [`assets/screenshot.png`](assets/screenshot.png)

## 5-minute Quickstart

### 1. Python

You need **Python 3.11 or newer** (`tomllib` is required):

- Windows: download from [python.org](https://www.python.org/downloads/), check "Add to PATH"
- Verify: `python --version` should print `Python 3.11.x`

### 2. Get the code

```bash
git clone https://github.com/<your-name>/codering_widget.git
cd codering_widget
```

Or just download the ZIP and extract to `D:\codering_widget\`.

### 3. Launch

```bash
python -m codex_tier_widget
```

Or:

```bash
python src/codex_tier_widget/widget.py
```

A 320×230 semi-transparent floating widget will pop up at the right-bottom corner of your screen immediately.

### 4. Usage

| Action | Effect |
|---|---|
| Drag the top bar | Move the window |
| Click a "Use this tier" button | Writes to `~/.codex/config.toml`; Codex restart required to take effect |
| Click ↻ Refresh | Immediately re-pull codexradar data |
| Right-click taskbar icon → Quit | Exit the program |

## Documentation Index

| Topic | File |
|---|---|
| Install & run | [INSTALL.md](INSTALL.md) |
| Full usage guide & shortcuts | [USAGE.md](USAGE.md) |
| How the 3 tiers are picked & color algorithm | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| FAQ | [docs/FAQ.md](docs/FAQ.md) |
| Contributing | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Version history | [CHANGELOG.md](CHANGELOG.md) |

## System Requirements

- **OS**: Windows 10 / 11 (macOS / Linux might work in theory, platform-specific bits untested)
- **Python**: 3.11+
- **Network**: Access to codexradar.com (for initial data pull)
- **Disk**: < 1MB
- **RAM**: < 50MB while running

## License

[MIT](LICENSE) — use, modify, redistribute, commercially, just keep the copyright notice.

## Contributing

PRs and Issues welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).
