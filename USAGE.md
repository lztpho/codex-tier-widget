# 使用说明 (Usage Guide)

## 1. 基本操作

### 1.1 启动 / 停止

| 动作 | 方法 |
|---|---|
| 启动 | `python -m codex_tier_widget` |
| 临时退出 | `Ctrl+C` 在启动它的终端窗口 |
| 永久退出 | 任务栏右键 Codex 图标 → Quit |
| 启动到自动最小化（tray） | 不支持（详见 [docs/FAQ.md](docs/FAQ.md)） |

### 1.2 悬浮窗交互

| 操作 | 效果 |
|---|---|
| **按住顶部条** 拖动 | 移动窗口到任意位置 |
| **点 "使用此档"** 按钮 | 弹确认框 → 确认 → 写 `~/.codex/config.toml` → 重启 Codex 生效 |
| **点 "↻ 刷新"** 按钮 | 立即拉一次 codexradar 新数据 |
| **点窗口右上角 ×**（如果有） | 隐藏窗口（保留 tray 图标） |

### 1.3 第 4 档 "当前档" 的显示规则

悬浮窗有 4 行（最后一个可能为空）：

```
[1] 普通档  推荐   → 按按钮切到这里
[2] 中等档  推荐   → 按按钮切到这里
[3] 高级档  推荐   → 按按钮切到这里
[4] 当前档  探测   → 实时显示你 Codex 正在用的档
                    但如果跟上面某档完全相同 → 整行不显示
```

举例：

| 你当前 Codex 设置 | 第 4 档显示 |
|---|---|
| `model=gpt-5-codex effort=xhigh` | **不显示**（因为这就是"普通档"） |
| `model=gpt-5-codex effort=high` | **显示**（橙黄底色，提示"这个档偏离推荐"） |
| `model=gpt-5-codex effort=low` | **显示**（红，提示"血亏"） |
| 未探测到 config.toml | 不显示 |

## 2. 配置自定义

### 2.1 改 3 个推荐档

编辑 `src/codex_tier_widget/config.py` 里的 `TIERS` 列表：

```python
TIERS = [
    {'name': '普通档', 'model': 'gpt-5.6-luna',  'effort': 'xhigh', 'tip': '...'},
    {'name': '中等档', 'model': 'gpt-5.6-terra', 'effort': 'xhigh', 'tip': '...'},
    {'name': '高级档', 'model': 'gpt-5.6-sol',   'effort': 'medium', 'tip': '...'},
]
```

`model` 是 codexradar 用名（参见 codexradar JSON），`effort` 是 `ultra/max/xhigh/high/medium/low` 之一。

重启 widget 生效。

### 2.2 改颜色阈值

编辑 `config.py` 里的 `COLOR_THRESHOLDS`：

```python
COLOR_THRESHOLDS = [
    (50, '#0e8c5b', '#d1f5ea'),  # ≥50 极绿
    (30, '#1e8449', '#daf5e3'),  # 30~50 纯绿
    (20, '#82c272', '#e8f5d8'),  # 20~30 黄绿
    ...
]
```

**含义**：(性价比阈值, 前景色, 背景色)。性价比 = IQ / price，≥ 阈值用最上面那一档。

### 2.3 改 MODEL_ALIAS（Codex CLI model 字符串映射）

如果你的 Codex CLI 用的是未在 `MODEL_ALIAS` 里的 model 字符串：

```python
MODEL_ALIAS = {
    'gpt-5-codex': 'gpt-5.6-sol',     # 默认
    'my-custom-model': 'gpt-5.6-sol', # <-- 加你自己的
    ...
}
```

### 2.4 改数据刷新间隔

```python
REFRESH_SECONDS  = 600   # codexradar 数据 10 分钟
POLL_INTERVAL_MS = 2000  # config.toml mtime 轮询 2 秒
```

## 3. 故障模式（graceful degradation）

工具遇到以下情况会自动降级，不会崩溃：

| 情况 | 行为 | 视觉 |
|---|---|---|
| 无网络（首次拉数据） | 用上次缓存 → 没有缓存显示「暂无数据」 | 灰色，全档位 |
| 无 ~/.codex/config.toml | 第 4 档不显示 | N/A |
| tomllib 解析失败 | fallback 正则匹配 | N/A |
| MODEL_ALIAS 没匹配 | 第 4 档显示「未知档 ⓘ」 | 灰 |
| Python < 3.11 | 程序仍能跑（用正则），但 console 打 warning | 灰 |

## 4. 多 Codex profile

如果你的 `~/.codex/config.toml` 用 `[profile.xxx]` 切多档：

```toml
[profile.dev]
model = "gpt-5-codex"
model_reasoning_effort = "high"

[profile.prod]
model = "gpt-5.6-sol"
model_reasoning_effort = "medium"
```

**当前版本不支持 profile 切换**——只读 [default] profile。

要支持的话，编辑 `codex_config.py` 的 `read()`，让它返回完整的 parsed dict，让你能在 widget 里点按钮切 `[profile.xxx]`。欢迎 PR。

## 5. 数据展示精度

| 字段 | 显示 |
|---|---|
| IQ | 整数（如果 ≥ 100）或 1 位小数（< 100） |
| 价格 | 2 位小数（$1.63 / $25.61） |
| 当前时间戳 | HH:MM |
| 数据更新时间戳 | 中文「3 分钟前」「昨天 22:31」 |

## 6. 注意事项

- **写 Codex config.toml 需要 Codex 重启才生效**——这是 OpenAI Codex CLI 自身的设计，悬浮窗无法解决
- **写入是原子的**（先 .tmp 再 os.replace），断电也不会半截文件
- **其他配置字段保留**——只动 `model` + `model_reasoning_effort` 两行
- **写入失败**（权限、文件占用）会显示「✗ 写入失败」，不抛异常
- **同时打开多个 widget 实例**有冲突（都盯同一个 config.toml），建议只开 1 个

## 7. 开发者

- 模块入口：[src/codex_tier_widget/__main__.py](../src/codex_tier_widget/__main__.py)
- UI 主类：[src/codex_tier_widget/widget.py](../src/codex_tier_widget/widget.py)
- 数据层：[src/codex_tier_widget/data.py](../src/codex_tier_widget/data.py)
- Codex 配置：[src/codex_tier_widget/codex_config.py](../src/codex_tier_widget/codex_config.py)
- 染色算法：[src/codex_tier_widget/color.py](../src/codex_tier_widget/color.py)
