"""codex_tier_widget — 桌面悬浮窗显示 Codex 档位 IQ / 价格。

常驻桌面右下角的悬浮窗，实时显示 Codex 三档推荐 + 一个「当前档」：
- 三档推荐（普通 / 中等 / 高级）按「IQ / 价格」性价比挑选
- 第 4 档「当前档」实时探测 `~/.codex/config.toml` 的 model 设置
- 按按钮 → 写 config.toml → 重启 Codex 后生效
- 染色：性价比越高越绿，越低越红

零外部依赖（仅 Python 3.11+ 标准库），整个项目 < 30KB。

启动：
    python -m codex_tier_widget

更多用法：[README.md](../../README.md) · [USAGE.md](../../USAGE.md)
"""

from __future__ import annotations

__version__ = '0.1.0'
__author__  = 'codering_widget contributors'
__license__ = 'MIT'

__all__ = [
    '__version__',
    '__author__',
    '__license__',
]
