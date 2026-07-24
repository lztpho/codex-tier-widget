"""公开跑测数据的读取、缓存与查找。"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

from . import config


def _normalize_model(value: object) -> str:
    """统一数据源可能附带的供应商前缀。"""
    if not isinstance(value, str):
        return ''
    model = value.strip().lower()
    for prefix in ('openai.', 'openai/', 'azure.'):
        if model.startswith(prefix):
            return model[len(prefix):]
    return model


def _normalize_effort(value: object) -> str:
    """统一数据源中不同的推理强度拼写。"""
    if not isinstance(value, str):
        return ''
    effort = value.strip().lower().replace('_', '-').replace(' ', '-')
    return {
        'extra-high': 'xhigh',
        'extra-highest': 'xhigh',
        'very-high': 'xhigh',
        'maximum': 'max',
    }.get(effort, effort)


def _http_get_json(url: str) -> dict:
    """获取并解析一个 JSON 对象。"""
    request = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'codex-tier-widget/0.1',
            'Accept': 'application/json',
        },
    )
    with urllib.request.urlopen(request, timeout=config.HTTP_TIMEOUT) as response:
        return json.loads(response.read().decode('utf-8'))


def save_cache(snapshot: dict, path: Path | None = None) -> None:
    """保存公开数据快照，供网络异常时使用。"""
    cache_path = path or config.DATA_CACHE
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(snapshot, ensure_ascii=False), encoding='utf-8')
    except OSError:
        pass


def load_cache(path: Path | None = None) -> dict | None:
    """读取本地快照；缓存不存在或损坏时返回空。"""
    cache_path = path or config.DATA_CACHE
    try:
        return json.loads(cache_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return None


def fetch_snapshot(use_cache_on_error: bool = True) -> dict | None:
    """获取最新公开数据；失败时回退到本地缓存。"""
    try:
        snapshot = _http_get_json(config.DATA_URL)
        save_cache(snapshot)
        return snapshot
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return load_cache() if use_cache_on_error else None


def find_point(snapshot: dict | None, model: str, effort: str) -> dict | None:
    """按模型名与推理强度查找对应的公开跑测记录。"""
    if not isinstance(snapshot, dict):
        return None
    points = snapshot.get('points')
    if not isinstance(points, list):
        return None

    wanted_model = _normalize_model(model)
    wanted_effort = _normalize_effort(effort)
    for point in points:
        if not isinstance(point, dict):
            continue
        actual_effort = point.get('effort', point.get('reasoning_effort'))
        if (
            _normalize_model(point.get('model')) == wanted_model
            and _normalize_effort(actual_effort) == wanted_effort
        ):
            return point
    return None
