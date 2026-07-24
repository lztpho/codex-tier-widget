"""codex_tier_widget.data — 拉 codexradar JSON + 离线缓存 + 查找 point。

数据源：https://codexradar.com/data/intelligence-efficiency.json
包含：
  - points: list of {model, effort, iq, average_price_usd, valid_tasks, total_runs, ...}
  - method: 评分公式说明（IQ = pass_rate × 150）
  - source_updated_at: 数据更新时刻
  - history: 历史快照（暂未使用，留作未来做趋势图）

错误处理策略：
  - 网络失败 → 尝试读磁盘缓存
  - 缓存也没有 → 返回 None
  - UI 用 None 表示「暂无数据」（灰色 + 文字提示）
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from . import config


# ─── 网络请求 ─────────────────────────────────────────────────────────────

def _http_get_json(url: str, *, timeout: tuple[float, float] | float = config.HTTP_TIMEOUT) -> dict:
    """HTTP GET 一个 JSON；返回解析后的 dict。

    Args:
        url:     URL
        timeout: (connect, read) 元组，或者单个值

    Raises:
        urllib.error.URLError / TimeoutError / json.JSONDecodeError
    """
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'codex-tier-widget/0.1 (+https://github.com/)',
            'Accept':     'application/json',
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read()
    return json.loads(body.decode('utf-8'))


# ─── 缓存 ──────────────────────────────────────────────────────────────────

def save_cache(snapshot: dict, path: Path | None = None) -> None:
    """把快照写本地缓存。"""
    cache_path = path or config.DATA_CACHE
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )
    except OSError:
        pass  # 缓存失败也不致命


def load_cache(path: Path | None = None) -> dict | None:
    """读本地缓存；不存在或损坏返回 None。"""
    cache_path = path or config.DATA_CACHE
    if not cache_path.exists():
        return None
    try:
        return json.loads(cache_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return None


# ─── 主入口：拉 + 缓存 fallback ──────────────────────────────────────────

def fetch_snapshot(use_cache_on_error: bool = True) -> dict | None:
    """拉 codexradar 当前快照；失败 fallback 缓存。

    Returns:
        snapshot dict（含 'points' / 'source_updated_at' 等字段）
        实在没有数据返回 None
    """
    # 1) 试网络
    try:
        snapshot = _http_get_json(config.DATA_URL)
        # 成功后顺手存缓存
        try:
            save_cache(snapshot)
        except Exception:
            pass
        return snapshot
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        # 2) fallback 缓存
        if use_cache_on_error:
            return load_cache()
        return None


# ─── 查找 ──────────────────────────────────────────────────────────────────

def find_point(snapshot: dict | None, model: str, effort: str) -> dict | None:
    """在 snapshot['points'] 里找 (model, effort) 对应的 point。

    Args:
        snapshot: fetch_snapshot() 返回值
        model:    模型名（codexradar 名，如 'gpt-5.6-sol'）
        effort:   推理强度（'low'/'medium'/'high'/'xhigh'/'max'/'ultra'）

    Returns:
        第一个匹配的 point dict，没找到返回 None
    """
    if not isinstance(snapshot, dict):
        return None
    points = snapshot.get('points')
    if not isinstance(points, list):
        return None
    for p in points:
        if not isinstance(p, dict):
            continue
        if p.get('model') == model and p.get('effort') == effort:
            return p
    return None


def all_points(snapshot: dict | None) -> list[dict]:
    """所有 point（按性价比降序排序），用于自定义档下拉。

    Returns:
        point 列表；snapshot 无效时返回 []
    """
    if not isinstance(snapshot, dict):
        return []
    points = snapshot.get('points')
    if not isinstance(points, list):
        return []
    from .color import score_for  # 避免循环
    scored = [(score_for(p), p) for p in points if isinstance(p, dict)]
    scored.sort(key=lambda x: -(x[0] or -1e9))
    return [p for _, p in scored]


# ─── 时间显示 ─────────────────────────────────────────────────────────────

def fresh_age_text(snapshot: dict | None) -> str:
    """数据新鲜度的文字描述，用于 UI 状态行。

    Returns:
        '刚刚' / '3 分钟前' / '2 小时前' / '数据未知'
    """
    if not isinstance(snapshot, dict):
        return '数据未知'
    s = snapshot.get('source_updated_at')
    if not isinstance(s, str):
        return ''
    # ISO 8601 形如 '2026-07-24T09:59:19+08:00'
    try:
        from datetime import datetime
        # 替换 +HH:MM 为时区偏移
        ts = s.replace('Z', '+00:00')
        dt = datetime.fromisoformat(ts)
        # 用 astimezone() 让两边都是 aware（避免 naive - aware 抛 TypeError）
        now = datetime.now().astimezone() if dt.tzinfo else datetime.now()
        delta = (now - dt).total_seconds()
        if delta < 0:
            return '数据未知'
        if delta < 60:
            return '刚刚'
        if delta < 3600:
            return f'{int(delta // 60)} 分钟前'
        if delta < 86400:
            return f'{int(delta // 3600)} 小时前'
        return f'{int(delta // 86400)} 天前'
    except Exception:
        return ''


def current_time_text() -> str:
    """本地时间 HH:MM。"""
    return time.strftime('%H:%M')


def updated_relative_text(snapshot: dict | None) -> str:
    """「数据更新于 X 分钟前」完整短语（用于状态行）。

    Returns:
        '刚刚更新' / '更新于 3 分钟前' / '数据未知'
    """
    age = fresh_age_text(snapshot)
    if not age:
        return '数据未知'
    if age == '刚刚':
        return '刚刚更新'
    if age == '数据未知':
        return '数据未知'
    return f'更新于 {age}'
