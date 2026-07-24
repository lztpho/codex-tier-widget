"""IQ 与费用的格式化及辅助颜色计算。"""

from __future__ import annotations

from . import config


def score_for(point: dict | None) -> float | None:
    """计算 IQ 与美元费用的比值。"""
    if not isinstance(point, dict):
        return None
    iq = point.get('iq')
    price = point.get('average_price_usd')
    if not isinstance(iq, (int, float)) or iq <= 0:
        return None
    if not isinstance(price, (int, float)) or price <= 0:
        return None
    return iq / price


def color_for(score: float | None) -> tuple[str, str]:
    """按性价比返回前景色与背景色。"""
    if score is None or score < 0:
        return config.GRAY_FG, config.GRAY_BG
    for threshold, foreground, background in config.COLOR_THRESHOLDS:
        if score >= threshold:
            return foreground, background
    return config.COLOR_THRESHOLDS[-1][1], config.COLOR_THRESHOLDS[-1][2]


def format_iq(iq: float | None) -> str:
    """格式化 IQ。"""
    if not isinstance(iq, (int, float)) or iq <= 0:
        return '—'
    return f'{iq:.0f}' if iq >= 100 else f'{iq:.1f}'


def format_price(price: float | None) -> str:
    """格式化美元费用。"""
    if not isinstance(price, (int, float)) or price <= 0:
        return '—'
    return f'${price:.2f}'
