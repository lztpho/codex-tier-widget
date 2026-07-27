"""公开跑测数据的读取、缓存与全量模型档位提取。"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

from . import config


def _http_get_json(url: str) -> dict:
    """获取并解析一个 JSON 对象。"""
    request = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'codex-tier-widget/0.4',
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


def all_points(snapshot: dict | None) -> list[dict]:
    """返回公开快照内全部有效的模型档位记录。"""
    if not isinstance(snapshot, dict):
        return []
    points = snapshot.get('points')
    if not isinstance(points, list):
        return []
    return [point for point in points if isinstance(point, dict)]
