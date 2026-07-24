# 常见问题 (FAQ)

> 提问前先看 [USAGE.md](../USAGE.md) 和 [docs/ARCHITECTURE.md](ARCHITECTURE.md)。

## 一般问题

### Q1: 这是 OpenAI 官方工具吗？

**不是**。这是第三方开源工具，不隶属于 OpenAI。

它读 `~/.codex/config.toml` 文件（Codex CLI 的标准配置位置）和 [codexradar.com](https://codexradar.com/) 的公开跑测数据，**不**连 OpenAI API、**不**发送你的代码到任何地方（除了拉 codexradar 公开 JSON 时）。

### Q2: 数据准确吗？会不会误导我？

codexradar.com 是第三方跑测站点，他们自己用 Codex CLI 真跑出来的 IQ/价格数据。每次拉数据时会显示「更新于 HH:MM」，是 codexradar 自己的更新时刻。

误差范围：±5 IQ 点（基于 ~330 跑测样本的中位波动）。所以**推荐档 I 内部**的差距（89.7 vs 93.8）可能没你以为的那么大；**档与档之间**（sol-ultra vs luna-xhigh）的差距是实打实的。

### Q3: 我用的是 Codex 桌面 App / VSCode 扩展，不通过 CLI，能用吗？

**降级可用**：

| 场景 | 行为 |
|---|---|
| 你 `codex` 命令能跑（Codex CLI） | 完整功能 |
| 你用 Codex 桌面 App | 第 4 档不显示；其他 3 档正常 |
| 你用 VSCode + Codex 扩展 | 第 4 档不显示；其他 3 档正常 |
| 你用网页版 chatgpt.com/codex | 第 4 档不显示；其他 3 档正常 |

将来可能支持桌面 App / VSCode 扩展联动，欢迎 PR。

## 安装相关

### Q4: 装完之后启动报 `AttributeError: module 'tomllib' not found`

Python 版本 < 3.11。装 3.11+ 或用 pyenv 切版本：

```bash
pyenv install 3.11
pyenv local 3.11
```

工具会**自动 fallback 到正则匹配**模式下运行，console 会打 warning。功能降级但能跑。

### Q5: 启动报 `ModuleNotFoundError: No module named 'tkinter'`

Linux / macOS 上 tkinter 不在默认 Python。装系统包：

```bash
# Debian / Ubuntu
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS (Homebrew Python)
brew install python-tk
```

Windows：重装 Python 时勾选 `tcl/tk and IDLE` 组件。

### Q6: 启动报 `IndentationError` 或 `SyntaxError`

你的 Python 版本太老（< 3.10）不支持 `from __future__ import annotations` 或 walrus operator。装 3.11+。

或者你改了源码——回 `git checkout` 恢复。

### Q7: 启动后白屏 / 窗口没出现

检查：

1. PyQt5/PySide6 等其他 GUI 框架的 tkinter 替代可能有的差异——本工具只用 tkinter
2. 高 DPI 缩放下窗口可能被推到屏幕外——编辑 `config.py` 把 `WINDOW_MARGIN` 改大
3. 多显示器环境主屏识别错误——临时把窗口拖回主屏

## 联动相关

### Q8: 按了按钮，悬浮窗状态「●已写入」，但 Codex 没切过去

确认 2 件事：

1. **重启 Codex CLI 进程**——本工具只写文件，不重启进程
   - 如果 Codex CLI 在终端运行：`Ctrl+C` 退出，再启动
   - 如果用 IDE 集成（如 Continue 插件）：重启 IDE

2. **检查 config.toml 内容**：
   ```bash
   cat ~/.codex/config.toml | grep -E "^(model|model_reasoning_effort)"
   ```
   应该看到两行覆盖了你刚选的 model + effort。

### Q9: 我手动改了 config.toml，但悬浮窗第 4 档没更新

mtime 轮询默认 2 秒一次。最坏延迟 2 秒。如果还看不到：

1. 确认你改的字段是 `model` 和 `model_reasoning_effort`（**不是 `[profile.xxx]` 里的同名字段**——本版本不支持）
2. 终端跑 `python -c "import codex_config; print(codex_config.read())"` 看是否能读到

### Q10: 提示「未知档 ⓘ」

Codex 用的 model 字符串不在 `MODEL_ALIAS` 里。打开 `config.py` 加一行：

```python
MODEL_ALIAS = {
    ...
    '你实际用到的字符串': 'gpt-5.6-sol',  # ← 对应的 codexradar 名
}
```

怎么查 codexradar 的 model 名？看 [codexradar.com](https://codexradar.com/) 顶部智力效率表那里写的什么 model 名。

### Q11: 当前档的 model 在 MODEL_ALIAS 里有映射，但染色颜色不对

确认两点：

1. **JSON 里 IQ 不是 0**——如果 codexradar 还没跑出这个 (model, effort) 的 IQ，IQ=0 → 视为无数据 → 灰色
2. **价格 > 0**——同样视为无数据 → 灰色

数据应该都已经有了（codexradar 自己实测验证过），如果还有问题开 Issue。

## 部署相关

### Q12: 能打包成单文件 .exe 吗？

当前版本没有打包（保持 0 依赖轻量）。如果需要 .exe 自行用 PyInstaller 打包：

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "Codex Tier Widget" src/codex_tier_widget/__main__.py
```

欢迎 PR 一个 GitHub Action 自动打包。

### Q13: 怎么在公司电脑上部署？

公司电脑通常：

- 没有 Python：装 Python 3.11+ (或者用 `py -3.11` 启动脚本)
- 没有 git：下载 ZIP 解压
- 网络限制（访问 codexradar 被拦）：改 `config.py` 的 `DATA_URL` 指向内网镜像（如果有）；或者用本地缓存方案

### Q14: 我有 2 个不同 Codex 账号（个人 / 公司），想同时跑 2 套

本版本只支持单 `~/.codex/config.toml`。两个账号需要：

1. 备份 / 切换 config.toml 文件的脚本
2. 同时跑 2 个 widget 实例（它们都会盯同一个 `~/.codex/config.toml`，**会有冲突**）

短期方案：用 `git diff` 维护两份配置，手动 `cp` 来回切换，再重启 widget。

长期方案：实现「profile 切换 + 多 widget 隔离」，欢迎 PR。

## 数据问题

### Q15: 数据是什么时候的？我怎么知道刷新了？

悬浮窗底部状态行 `↻ 刷新 · 选中: ●普通档` 旁边的「●已连接 / ●延迟」标记：

| 标记 | 含义 |
|---|---|
| `●实时连动` | 数据 < 30 分钟前 |
| `●延迟`（橙色） | 数据 30 分钟 - 2 小时前 |
| `●离线`（红色） | 数据 > 2 小时前 |

（具体阈值在 `widget.py` 里改）

### Q16: 我想换 codexradar 之外的 IQ 数据源（比如 LMSYS Arena、OpenAI 官方 benchmark）

当前不支持，但接口设计预留了扩展点。把 `data.py` 里的 `fetch_snapshot()` 替换成新源即可（保证返回 `points` 字段格式一致即可）。

欢迎 PR 让你更喜欢的 IQ 数据源做后端。

## 其他

### Q17: 怎么完全卸载？

1. 关闭 widget
2. 删除项目目录：`rm -rf D:\codering_widget`
3. 可选：清理缓存文件 `~/.codex_radar_cache.json`
4. **不**撤销对 `~/.codex/config.toml` 的修改——你自己改回即可（或者直接 `git checkout`）

### Q18: 工具会发送我的代码内容到任何服务器吗？

**不会**。本工具不连 OpenAI API、不会读你的代码文件、不会发任何 prompt 给外部。

唯一的网络请求：每 10 分钟 GET 一次 `codexradar.com/data/intelligence-efficiency.json`（公开数据，~350KB）。

### Q19: 工具被杀毒误报怎么办？

工具用 tkinter 写文件，无可执行代码、无加密、无网络连接、无敏感 API 调用。如果某天打包成 .exe 被误报，加白名单或参考 [PyInstaller 误报问题](https://github.com/pyinstaller/pyinstaller/issues/4699)。

### Q20: 怎么贡献 PR / 翻译？

看 [CONTRIBUTING.md](../CONTRIBUTING.md)。翻译直接 PR `README.en.md` 或新加 `README.<lang>.md`。
