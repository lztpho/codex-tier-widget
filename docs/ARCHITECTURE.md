# 架构 (Architecture)

> 给想深入理解项目 / 想贡献代码的人。读完后能画出每个模块的依赖关系。

## 1. 设计目标

| 目标 | 体现 |
|---|---|
| **轻量便携** | 0 外部依赖，整个项目 < 30KB |
| **跨机部署** | 整个 `D:\codering_widget\` 拷走就能跑 |
| **实时数据** | 10 分钟级 codexradar 拉数，2 秒级 mtime 轮询 |
| **真联动** | 写 `~/.codex/config.toml` 让 Codex 重启后切换 |
| **视觉清晰** | 价格/IQ/性价比染色一眼可读 |

## 2. 模块依赖图

```
┌────────────────────────────────────────────────────────────┐
│                       widget.py                            │
│    (tkinter 主循环: UI 构建、tick 调度、用户交互)              │
└────┬──────────────────┬────────────────┬──────────────────┘
     │                  │                │
     │ use              │ refresh        │ tick
     ▼                  ▼                ▼
┌──────────┐     ┌────────────┐    ┌──────────┐
│codex_    │     │ data.py    │    │ config.py│
│config.py │     │ (拉数据+   │    │ (静态配置)│
│ (读写    │     │  缓存)     │    └──────────┘
│  config  │     └─────┬──────┘
│  .toml)  │           │
└────┬─────┘           │ cache
     │                 ▼
     │           ┌──────────┐
     │           │  缓存    │
     │           │ ~/.codex │
     │           │ _radar_  │
     │           │ cache.   │
     │           │ json     │
     │           └──────────┘
     │                 │
     ▼                 ▼
   ~/.codex/      codexradar.com
   config.toml    /data/intelligence-
                  efficiency.json
                        │
                        ▼
                  ┌──────────┐
                  │ color.py │
                  │ (IQ/$    │
                  │  → 颜色) │
                  └──────────┘
                        │
                        ▼
                     widget.py
                     (画 UI)
```

### 2.1 模块职责

| 模块 | 职责 | 行数（约） |
|---|---|---|
| `widget.py` | tkinter UI 主循环 + 4 档渲染 + 按钮事件 + 定时 tick | ~280 |
| `data.py` | 拉 codexradar + 缓存 + 解析（按 model+effort 查 IQ/price） | ~80 |
| `codex_config.py` | 读/写 `~/.codex/config.toml` + mtime 监测 + 原子写 | ~110 |
| `color.py` | 性价比（IQ/$）→ 颜色 hex（绝对阈值映射） | ~30 |
| `config.py` | TIERS + MODEL_ALIAS + COLOR_THRESHOLDS + URL/路径常量 | ~80 |

### 2.2 调用方向

- `widget.py` 是顶层，**唯一**进入应用的方式
- 其他模块**不** import widget.py（避免循环依赖）
- `config.py` 是叶子，被所有模块读，但**不** import 任何东西
- `color.py` 只依赖 `config.py`

## 3. 数据流 (Data Flow)

### 3.1 启动流程

```
python -m codex_tier_widget
  ↓
__main__.py: main()
  ↓
TierWidget.__init__()
  ├── 创建 tk.Tk() 窗口 (frameless + alpha + topmost)
  ├── 构造 CodexConfig (探 ~/.codex/config.toml mtime)
  ├── 构造 TierRow × 3 (3 个推荐档)
  ├── 构造 CurrentRow × 1 (第 4 档，默认隐藏)
  ├── refresh_data() 同步拉一次 codexradar
  └── tick() 注册 2 秒后回调
  ↓
tk.mainloop()
```

### 3.2 数据刷新（10 分钟周期）

```
tick() 回调触发
  ↓
距 last_refresh > REFRESH_SECONDS?
  ├── 是 → refresh_data()
  │     ├── 读缓存 fallback → DATA_URL 拉 JSON
  │     ├── 解析 snapshot['points']
  │     ├── 对 4 档算 IQ/价格/性价比
  │     ├── color_for(score) → (fg, bg)
  │     └── 重绘 4 行
  └── 否 → 跳过
```

### 3.3 用户按按钮

```
"使用此档" 按钮
  ↓
弹 messagebox.askyesno() 确认
  ├── 否 → return
  └── 是
       ↓
     CodexConfig.write(model, effort)
       ├── 读 ~/.codex/config.toml
       ├── re 替换 model / model_reasoning_effort 两行
       ├── 原子写 .tmp + os.replace()
       └── 返回 True/False
     ↓
     更新 status 行: "●已写入" 或 "✗ 写入失败"
     ↓
     2 秒后 tick() 检测到 mtime 变化
     ↓
     _refresh_current_tier() 重读
     ↓
     如果新写的正好等于某个推荐档 → 第 4 档 hide()
     否则 → 第 4 档 show()
```

### 3.4 用户手动切档（Codex UI 里改）

```
用户在 Codex 桌面 UI 选 "gpt-5-codex / low"
  ↓
Codex 写 ~/.codex/config.toml (更新 mtime)
  ↓
~2 秒后 widget tick() 发现 mtime 变了
  ↓
_refresh_current_tier()
  ├── codex.read() 拿到 {model: "gpt-5-codex", effort: "low"}
  ├── MODEL_ALIAS 解析 model → "gpt-5.6-sol"
  ├── find_point(snapshot, "gpt-5.6-sol", "low")
  │     找到 IQ=79.0, price=$2.03, score=38.9
  ├── 与 TIERS 比对：不等任何推荐档
  └── CurrentRow.show()
        └── 重绘第 4 档（绿色背景，IQ 79, $2.03/次）
```

## 4. 关键算法

### 4.1 三档推荐是怎么挑的（参见项目决策）

来源：[codexradar.com](https://codexradar.com/) 实时 IQ 跑测数据。

**挑选原则**：

| 档位 | 任务类型 | 挑选 |
|---|---|---|
| 普通档 | 单文件 < 300 行、调试 | 最便宜的可用档（IQ ≥ 80 + 价格最低） |
| 中等档 | 跨文件、控制环 | 价格翻倍 + IQ 提升 5+ 的档 |
| 高级档 | 架构、debug | IQ ≥ 90 中最便宜的档 |

IQ 阈值取自工程经验：「IQ 80 以下会明显返工、90+ 才能放心写复杂逻辑」。

详细推导参见 [USAGE.md § 2](../USAGE.md)。

### 4.2 染色算法

**公式**：`score = iq / price`（单位 IQ per USD）

**映射**：绝对阈值（不归一化）。

| 阈值 (score) | 颜色对（fg, bg）| 含义 |
|---|---|---|
| ≥ 50 | 极绿 | 「白给」档，错过血亏 |
| 30 ~ 50 | 纯绿 | 极佳推荐 |
| 20 ~ 30 | 黄绿 | 不错但不是爆款 |
| 10 ~ 20 | 橙黄 | 一般，性价比中等 |
| 5 ~ 10 | 橙红 | 偏贵，建议改档 |
| < 5 | 红 | 血亏档，确认是不是手滑 |

**为什么不用 min-max 全局归一化？**

全局 min-max 会把所有档位拉成「均匀分布」，推荐档内部也会呈现「极绿 / 绿 / 淡黄」混合的色阶，**视觉上推荐档不再"清一色绿"**，反而让用户觉得推荐不靠谱。

绝对阈值保证：

- 3 个推荐档**永远在绿色系**（只要 IQ/price ≥ 20 就是绿）
- 自定义 / 当前档如果选错了（比如 sol ultra），明显发红，**一眼看见**

### 4.3 mtime 轮询

```python
POLL_INTERVAL_MS = 2000  # 2 秒

def tick(self):
    current_mtime = self.codex.mtime()  # 读 ~/.codex/config.toml 的 st_mtime
    if current_mtime != self.codex.last_mtime:
        self.codex.last_mtime = current_mtime
        self._refresh_current_tier()
    self.root.after(POLL_INTERVAL_MS, self.tick)
```

**为什么 2 秒**？

- 1 秒：太频繁，磁盘 IO 多
- 5 秒：用户感知到延迟
- 2 秒：磁盘 IO 几乎无成本（每个 tick 只读一个 stat）

**为什么不用 watchdog/fswatch？**

- 0 依赖路线，避开了额外包
- tkinter after() 自带，跨平台

### 4.4 原子写

```python
tmp = path.with_suffix('.toml.tmp')
tmp.write_text(text, encoding='utf-8')
os.replace(tmp, path)  # POSIX 是原子的，Windows 自 Vista 起也是原子的
```

防止写一半断电 / 进程被杀 → 留下半截坏文件。

## 5. 错误处理

每层错误独立处理，不抛到顶层：

| 层 | 错误 | 处理 |
|---|---|---|
| `data.fetch_snapshot()` | 网络错 / JSON 解析错 | 返回 None；调用方 fallback 缓存 |
| `codex_config.read()` | 文件不存在 / 权限 | 返回 None |
| `codex_config.write()` | 权限 / 占用 | 返回 False，UI 显示「✗ 写入失败」 |
| `color.color_for()` | score=None | 返回灰色 |
| `widget.tick()` | 任何异常 | `try/except` 包住，log，不中断主循环 |

**核心理念**：网络/IO 错误不应该杀掉用户的悬浮窗。

## 6. 线程模型

**单线程**。tkinter + after() 已经在主线程上做消息循环，子线程 + tkinter 容易出问题。

CPU / IO 都是轻量的（一个 HTTP GET + 几次文件 stat），不需要 async。

如果未来要支持「按按钮后异步轮询 Codex 进程是否启动」，再考虑 `threading.Thread` + `root.after()` poll。

## 7. 性能预算

| 操作 | 期望耗时 |
|---|---|
| 启动到首帧 | < 500ms |
| HTTP GET codexradar | < 1s |
| mtime stat | < 10ms |
| 重绘 4 行 | < 50ms |
| 写 config.toml | < 10ms |
| 内存占用 | < 50MB |

实测：以上都达预期。如有偏差开 Issue。

## 8. 未来扩展

| 想法 | 难度 | 影响 |
|---|---|---|
| 单元测试套件 | 中 | 提升可维护性 |
| 系统托盘（pystray） | 低 | 体验更完整，但要加依赖 |
| 支持 `[profile.xxx]` | 中 | 多账号场景 |
| 通知 API（用户切了 Codex 给我推一条） | 高 | 跨进程 IPC |
| Codex 桌面 App 联动 | 高 | 需要逆向它的配置文件位置 |
| 自动重启 Codex 进程 | 低 | 体验好，但风险大（中断工作流） |

## 9. 安全考虑

- **不连 OpenAI API**：工具不发任何 prompt / code 内容
- **不连任何第三方 tracker**：除 codexradar
- **写文件白名单**：只动 `~/.codex/config.toml` 的两行
- **原子写**：避免半截文件
- **try/except 包住所有 IO**：不让单次失败杀死进程
- **不使用 sub-process**：没有任何 shell exec 调用

详见 [SECURITY.md](../SECURITY.md)（如有）。
