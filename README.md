# Codex Tier Widget

> 一个常驻 Windows 桌面右下角的悬浮窗，实时显示 Codex 三档推荐的 IQ + 价格 + 性价比染色，按按钮直接切换 Codex 当前档位。

[English README →](README.en.md)

## 这是什么

如果你用 OpenAI Codex 写代码，每次都要纠结「这次任务该用哪个模型档位」——这个工具就是为这个场景做的：

- **常驻桌面**：右下角浮动小窗，frameless + 半透 + always-on-top，不抢屏幕
- **实时数据**：每 10 分钟拉一次 [codexradar.com](https://codexradar.com/) 的 IQ 跑测数据，自动分析
- **一档对一档**：3 个推荐档位（普通 / 中等 / 高级）按「IQ / 价格」性价比已挑选好
- **真联动**：按按钮 → 直接改写 `~/.codex/config.toml`，Codex 重启生效
- **配色**：性价比越高越绿，越差越红——一眼看出来有没有选错档
- **0 外部依赖**：纯 Python 3.11+ 标准库，整个项目 < 30KB

## 截图占位

```
┌──────────────────────────────────┐
│ Codex 档位 · 21:34   ●实时连动    │ ← 状态行
│ ──────────────────────────────── │
│ 🟢 普通档                       │
│   luna xhigh        IQ 84.4      │
│   $1.63 / 次      [ 使用此档 ]   │
│ ──────────────────────────────── │
│ 🟡 中等档                       │
│   terra xhigh       IQ 89.7      │
│   $2.36 / 次      [ 使用此档 ]   │
│ ──────────────────────────────── │
│ 🟠 高级档                       │
│   sol medium        IQ 93.8      │
│   $3.69 / 次      [ 使用此档 ]   │
│ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │
│ ⚙️ 当前档  (你正在用 Codex)        │
│   gpt-5-codex high  IQ 87.1      │
│   $5.87 / 次                     │
│ ──────────────────────────────── │
│ ↻ 刷新 · 选中: ●普通档            │
└──────────────────────────────────┘
```

> 真实运行截图见 [`assets/screenshot.png`](assets/screenshot.png)（首次发布时附）

## 5 分钟上手

### 1. 准备 Python

需要 **Python 3.11 或更新版本**（用到 `tomllib`）：

- Windows: 从 [python.org](https://www.python.org/downloads/) 下载安装，勾选「Add to PATH」
- 验证：`python --version` 应返回 `Python 3.11.x`

### 2. 拉取项目

```bash
git clone https://github.com/<your-name>/codering_widget.git
cd codering_widget
```

> 也可以直接下载 ZIP 解压到 `D:\codering_widget\`

### 3. 启动

```bash
python -m codex_tier_widget
```

或者：

```bash
python src/codex_tier_widget/widget.py
```

启动后桌面右下角会立即弹出 320×230 的半透悬浮窗。

### 4. 用法

| 动作 | 效果 |
|---|---|
| 按住顶部拖动 | 移动窗口 |
| 点「使用此档」按钮 | 写入 `~/.codex/config.toml`，需要重启 Codex 生效 |
| 点「↻ 刷新」 | 立即拉一次 codexradar 新数据 |
| 关闭（任务栏右键退出） | 退出程序 |

## 文档索引

| 想了解 | 看哪里 |
|---|---|
| 怎么装、怎么跑 | [INSTALL.md](INSTALL.md) |
| 详细使用说明、快捷键、所有参数 | [USAGE.md](USAGE.md) |
| 三档推荐是怎么挑出来的？染色算法？ | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| 常见问题 | [docs/FAQ.md](docs/FAQ.md) |
| 想贡献代码 | [CONTRIBUTING.md](CONTRIBUTING.md) |
| 版本变化 | [CHANGELOG.md](CHANGELELOG.md) |

## 系统要求

- **OS**: Windows 10 / 11（macOS / Linux 理论上能用，平台特性没测）
- **Python**: 3.11+
- **网络**: 需要访问 codexradar.com（首次拉数据时）
- **磁盘**: < 1MB
- **内存**: < 50MB 运行

## 开源 License

[MIT](LICENSE) — 随便用、改、商用，只需要保留版权声明。

## 贡献

欢迎 PR / Issue！详见 [CONTRIBUTING.md](CONTRIBUTING.md)。
