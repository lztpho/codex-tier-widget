# 使用说明

## 界面与操作

悬浮窗固定显示三行，每行只有模型短名称、IQ 和费用。它没有按钮、当前档状态或模型切换功能。

- 按住任意模型行拖动窗口。
- 按 Escape 关闭窗口。
- 窗口在启动时显示于屏幕右下角，并始终置顶。

## 数据更新

程序启动时请求一次公开数据，之后每 10 分钟再次请求。请求失败时会读取 `~/.codex_radar_cache.json`；缓存也不可用时，IQ 和费用显示为 `—`。

数据更新后，三行会自动重新排序。

## 排名逻辑

默认最低 IQ 为 80。

| 情况 | 排名方式 |
| --- | --- |
| IQ ≥ 80 | 按 `IQ ÷ 费用` 从高到低 |
| IQ < 80 | 排在所有达标模型之后，再按 `IQ ÷ 费用` 从高到低 |
| 缺失 IQ 或费用 | 固定排在最后 |

可在 [config.py](D:/codering_widget/src/codex_tier_widget/config.py) 修改门槛：

```python
MINIMUM_IQ = 80.0
```

## 修改显示档位

同一配置文件的 `TIERS` 控制展示的三个档位：

```python
TIERS = [
    {'label': '5.6-luna-max', 'model': 'gpt-5.6-luna', 'effort': 'max'},
    {'label': '5.6-terra-max', 'model': 'gpt-5.6-terra', 'effort': 'max'},
    {'label': '5.6-sol-medium', 'model': 'gpt-5.6-sol', 'effort': 'medium'},
]
```

`label` 为窗口中的文字；`model` 与 `effort` 必须能与数据源对应。界面固定为三行，修改后请重启悬浮窗。

## 数据与颜色

费用文字和左侧细条使用 IQ÷费用的颜色提示：绿色表示相对更高，黄色或红色表示相对更低。颜色仅用于辅助阅读，不会替代排名逻辑。

程序仅使用 Codex 雷达公开数据和本机缓存；不会读取或写入 Codex 配置。
