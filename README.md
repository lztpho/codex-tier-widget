# Codex 档位展示窗

一个紧凑、无标题栏、始终置顶的桌面悬浮窗。它会从 Codex 雷达全部公开模型档位中计算排名，只展示前三名的模型短名称、IQ 与费用。

```text
5.6-luna-xhigh   IQ84.4    $1.63
5.6-terra-xhigh  IQ91.1    $2.35
5.6-luna-max     IQ85.7    $2.52
```

项目只展示公开跑测数据：不读取、不修改 Codex 配置，不切换模型，也不重启或控制 Codex。

## 特性

- 仅显示必要信息：模型短名称、IQ、美元费用。
- 紧凑三行界面，可按住任意一行拖动；按 Escape 关闭。
- 启动时拉取数据，之后每 10 分钟刷新一次；网络异常时使用本机缓存。
- 每次刷新都对全部公开模型档位计算排序，只显示前三名。
- IQ 达到 80 的模型按 `IQ ÷ 费用` 从高到低排序；IQ 未达标或无数据的模型靠后。
- 仅使用 Python 标准库，无额外运行依赖。

## 快速开始

需要 Windows 10/11 与 Python 3.11 或更新版本。在项目根目录运行：

```powershell
python scripts/launch_widget.py
```

窗口启动后出现在屏幕右下角。按住模型行拖动，按 Escape 关闭。

## 排名规则

`MINIMUM_IQ = 80` 是能力门槛。

1. IQ 达到 80 的档位排在前面。
2. 达标档位按 `IQ ÷ average_price_usd` 从高到低排序。
3. IQ 未达标的档位排在后面，同样按性价比排序。
4. 数据缺失的档位始终排在最后。

这样不会因为费用低而优先推荐能力不足的模型，同时仍会在可用模型中优先展示性价比更高的选择。

## 自定义排名门槛

编辑 [config.py](D:/codering_widget/src/codex_tier_widget/config.py)：

```python
MINIMUM_IQ = 80.0
DISPLAY_LIMIT = 3
```

`MINIMUM_IQ` 决定能力门槛；`DISPLAY_LIMIT` 保持为 3，以维持紧凑三行界面。修改后重启悬浮窗即可。

## 数据与隐私

数据来自 [Codex 雷达](https://codexradar.com/) 的公开智力效率数据。程序只会在本机写入数据缓存 `~/.codex_radar_cache.json`，不会访问 `~/.codex/config.toml`，也不会上传代码、提示词或账户信息。

## 开发校验

```powershell
python tools/dev_check.py all
python tools/release_check.py
```

更多内容见 [安装指南](D:/codering_widget/INSTALL.md)、[使用说明](D:/codering_widget/USAGE.md)、[架构说明](D:/codering_widget/docs/ARCHITECTURE.md)、[常见问题](D:/codering_widget/docs/FAQ.md) 与 [贡献指南](D:/codering_widget/CONTRIBUTING.md)。
