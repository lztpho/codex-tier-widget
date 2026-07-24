# 更新日志 (Changelog)

> 所有重要变更按 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 规范记录。

## [Unreleased]

### 已计划
- 系统托盘图标支持（pystray，可选依赖）
- macOS / Linux 兼容性测试
- 打包成 .exe（PyInstaller，可选构建）
- 单元测试套件

## [0.1.0] - 2026-07-24

### 新增

- 🎉 首版发布
- **三档推荐**：普通档 / 中等档 / 高级档，按「IQ / 价格」性价比挑选
- **第 4 档「当前档」实时探测**：从 `~/.codex/config.toml` 读取 Codex 当前档
  - 如果等于某个推荐档 → 整行隐藏
  - 否则显示 IQ + 价格 + 染色
- **真联动**：按按钮 → 原子写 `~/.codex/config.toml`，Codex 重启生效
- **实时数据**：每 10 分钟拉 [codexradar.com](https://codexradar.com/) 的 IQ 跑测
- **染色算法**：绝对阈值映射红-黄-绿，越绿性价比越好
  - 推荐档全部稳定在绿色系
  - 当前档选偏贵了明显红/黄
- **2 秒 mtime 轮询**：用户在 Codex 桌面 UI 手动切换档，悬浮窗 2 秒内反映
- **0 外部依赖**：纯 Python 3.11+ 标准库
- **完整文档**：README (中/英) + INSTALL + USAGE + CONTRIBUTING + docs/ARCHITECTURE + docs/FAQ
- **MIT License**：开源、可商用
- **Git 骨架**：.github/ISSUE_TEMPLATE + .github/workflows/syntax-check.yml

### 已验证

- Windows 11 + Python 3.11+ 启动正常
- `~/.codex/config.toml` 读写功能
- codexradar JSON 拉取 + 解析
- 浮窗 320×230 frameless + 半透 + always-on-top

### 已知限制

- Codex CLI 不重启不生效（Codex 自身限制）
- OpenAI model 名 → codexradar 档案 model 名 映射有 4 个默认值，用户需实测后调整
- 不支持 `[profile.xxx]` 多 profile（详见 USAGE.md § 4）
- 不支持系统托盘（悬浮窗点击 × 隐藏）

### 修复（commit 之前发现并修掉）

- `data.fresh_age_text()`：原本用 `datetime.now()`（naive）去减 `datetime.fromisoformat(...)`（aware，会带 `+08:00`），抛 `TypeError` 被 try/except 吞，状态行始终显示空。修复为 `datetime.now().astimezone()`，保证两边都是 aware。
