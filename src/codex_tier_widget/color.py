"""性价比计算、显示格式和深色界面颜色。"""

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


def price_color_for(score: float | None) -> str:
    """根据性价比分数返回深色界面中的文字颜色。"""
    if score is None:
        return config.MUTED_FG
    if score >= 30:
        return config.PRICE_GOOD_FG
    if score >= 20:
        return config.PRICE_MID_FG
    if score >= 10:
        return config.PRICE_WARN_FG
    return config.PRICE_BAD_FG


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
