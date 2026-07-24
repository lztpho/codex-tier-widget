"""codex_tier_widget.color — 性价比 → 颜色映射。

按用户的「更省钱」策略：用 **绝对阈值**（不用 min-max 归一化）。
这样：
  - 3 个推荐档全部稳定在绿色系（极绿/纯绿/黄绿）
  - 当前档或自定义档如果选贵了（sol xhigh / sol ultra）明显变黄/红

性能公式：score = IQ / average_price_usd（单位 IQ per USD）。

阈值表在 `config.py` 的 COLOR_THRESHOLDS，用户可改。

更多说明：[docs/ARCHITECTURE.md § 4.2](../../docs/ARCHITECTURE.md)
"""

from __future__ import annotations

from . import config


def score_for(point: dict | None) -> float | None:
    """从 codexradar 的 point dict 算「性价比」分数。

    Args:
        point: 形如
            {'iq': 90, 'average_price_usd': 3.0, ...}

    Returns:
        IQ / price（float），任何字段缺失返回 None
    """
    if not isinstance(point, dict):
        return None
    iq = point.get('iq')
    price = point.get('average_price_usd')
    if iq in (None, 0) or not isinstance(price, (int, float)) or price <= 0:
        return None
    return iq / price


def color_for(score: float | None) -> tuple[str, str]:
    """性价比 → (前景色 hex, 背景色 hex)。

    Args:
        score: score_for() 返回的性价比；None 表示无数据

    Returns:
        (fg, bg) — tkinter 兼容的 hex 字符串
    """
    if score is None or score < 0:
        return config.GRAY_FG, config.GRAY_BG

    # 自上而下扫描，命中第一个 ≥ threshold 的档
    for threshold, fg, bg in config.COLOR_THRESHOLDS:
        if score >= threshold:
            return fg, bg

    # 全部不命中 → 用最后一档（最差颜色）
    return config.COLOR_THRESHOLDS[-1][1], config.COLOR_THRESHOLDS[-1][2]


def format_iq(iq: float | None) -> str:
    """格式化 IQ 显示。"""
    if iq is None or iq == 0:
        return '—'
    if iq >= 100:
        return f'{iq:.0f}'
    return f'{iq:.1f}'


def format_price(price: float | None) -> str:
    """格式化价格显示。"""
    if price is None or price == 0:
        return '—'
    return f'${price:.2f}'


def format_score(score: float | None) -> str:
    """格式化性价比（调试用）。"""
    if score is None:
        return '—'
    return f'{score:.1f}'
