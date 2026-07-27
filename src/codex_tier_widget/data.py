"""公开跑测数据的读取、缓存与全量模型档位提取。"""

from __future__ import annotations

import json
import math
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

from . import config

COMBINED_COST_WEIGHT = math.log(2.5) / math.log(1.35)


def _http_get_json(url: str) -> dict:
    """获取并解析一个 JSON 对象。"""
    request = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'codex-tier-widget/0.4.1',
            'Accept': 'application/json',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        },
    )
    with urllib.request.urlopen(request, timeout=config.HTTP_TIMEOUT) as response:
        return json.loads(response.read().decode('utf-8'))


def _finite_number(value: object) -> float | None:
    """把 JSON 数字转换为有限浮点数，并排除布尔值。"""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _timestamp(value: object) -> float | None:
    """把 ISO 时间转换成便于比较的时间戳。"""
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.timestamp()


def aggregate_table(payload: dict) -> dict:
    """按 Codex 雷达网页规则把实时任务表聚合成模型档位数据。"""
    combos = payload.get('combos')
    tasks = payload.get('tasks')
    cells = payload.get('cells')
    if not isinstance(combos, list) or not combos:
        raise ValueError('实时数据缺少模型档位')
    if not isinstance(tasks, list) or not tasks:
        raise ValueError('实时数据缺少任务')
    if not isinstance(cells, dict):
        raise TypeError('实时数据缺少任务结果')

    points: list[dict] = []
    source_updated_at: float | None = None

    for combo in combos:
        if not isinstance(combo, dict):
            continue
        model = str(combo.get('model') or '').strip()
        effort = str(combo.get('effort') or '').strip()
        if not model or not effort:
            continue

        passed = 0
        valid_tasks = 0
        duration_sum = 0.0
        duration_samples = 0
        price_sum = 0.0
        price_samples = 0
        incomplete_cost_samples = 0
        total_runs = 0
        latest_graded_at: str | None = None
        latest_graded_timestamp: float | None = None
        agent_steps_sum = 0.0
        agent_steps_samples = 0
        total_tokens_sum = 0.0
        token_samples = 0
        input_tokens_sum = 0.0
        cache_tokens_sum = 0.0
        cache_token_samples = 0

        for task in tasks:
            if not isinstance(task, dict) or task.get('id') is None:
                continue
            key = f"{task['id']}|{model}|{effort}"
            cell = cells.get(key)
            if not isinstance(cell, dict):
                continue
            runners = cell.get('ran_by')
            if not isinstance(runners, list):
                continue

            total_runs += sum(isinstance(item, dict) for item in runners)
            runner = runners[0] if runners else None
            if not isinstance(runner, dict):
                continue

            result = runner.get('passed')
            if isinstance(result, bool):
                valid_tasks += 1
                passed += int(result)

            duration = _finite_number(runner.get('duration_sec'))
            if duration is not None and duration > 0:
                duration_sum += duration / 60
                duration_samples += 1

            price = _finite_number(runner.get('actual_cost_usd'))
            if price is not None and price >= 0:
                if effort != 'ultra' or runner.get('cost_complete') is True:
                    price_sum += price
                    price_samples += 1
                else:
                    incomplete_cost_samples += 1

            graded_at = runner.get('graded_at')
            graded_timestamp = _timestamp(graded_at)
            if graded_timestamp is not None:
                if source_updated_at is None or graded_timestamp > source_updated_at:
                    source_updated_at = graded_timestamp
                if latest_graded_timestamp is None or graded_timestamp > latest_graded_timestamp:
                    latest_graded_timestamp = graded_timestamp
                    latest_graded_at = str(graded_at)

            agent_steps = _finite_number(runner.get('n_agent_steps'))
            if agent_steps is not None and agent_steps >= 0:
                agent_steps_sum += agent_steps
                agent_steps_samples += 1

            input_tokens = _finite_number(runner.get('n_input_tokens'))
            output_tokens = _finite_number(runner.get('n_output_tokens'))
            cache_tokens = _finite_number(runner.get('n_cache_tokens'))
            if input_tokens is not None or output_tokens is not None:
                total_tokens_sum += max(0.0, input_tokens or 0.0)
                total_tokens_sum += max(0.0, output_tokens or 0.0)
                token_samples += 1
            if (
                input_tokens is not None
                and input_tokens > 0
                and cache_tokens is not None
                and cache_tokens >= 0
            ):
                input_tokens_sum += input_tokens
                cache_tokens_sum += cache_tokens
                cache_token_samples += 1

        if not valid_tasks:
            continue

        points.append(
            {
                'model': model,
                'effort': effort,
                'passed': passed,
                'valid_tasks': valid_tasks,
                'iq': passed / valid_tasks * 150,
                'average_price_usd': price_sum / price_samples if price_samples else None,
                'price_samples': price_samples,
                'average_minutes': duration_sum / duration_samples if duration_samples else None,
                'duration_samples': duration_samples,
                'incomplete_cost_samples': incomplete_cost_samples,
                'total_runs': total_runs,
                'latest_graded_at': latest_graded_at,
                'average_agent_steps': agent_steps_sum / agent_steps_samples
                if agent_steps_samples
                else None,
                'agent_steps_samples': agent_steps_samples,
                'average_total_tokens': total_tokens_sum / token_samples if token_samples else None,
                'token_samples': token_samples,
                'cache_hit_rate': cache_tokens_sum / input_tokens_sum
                if cache_token_samples and input_tokens_sum > 0
                else None,
                'cache_token_samples': cache_token_samples,
            }
        )

    if not points:
        raise ValueError('实时数据没有可用模型档位')

    for point in points:
        price = point['average_price_usd']
        minutes = point['average_minutes']
        point['raw_combined_cost'] = (
            price * math.pow(minutes / 10, COMBINED_COST_WEIGHT) * 100
            if price is not None and price > 0 and minutes is not None and minutes > 0
            else None
        )

    max_raw_cost = max((point['raw_combined_cost'] or 0.0) for point in points)
    for point in points:
        raw_cost = point['raw_combined_cost']
        point['combined_cost_index'] = (
            raw_cost / max_raw_cost * 100 if raw_cost is not None and max_raw_cost > 0 else None
        )

    updated = datetime.fromtimestamp(source_updated_at, UTC) if source_updated_at else None
    return {
        'points': points,
        'source_updated_at': updated.isoformat() if updated else None,
    }


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
        snapshot = aggregate_table(_http_get_json(config.DATA_URL))
        save_cache(snapshot)
        return snapshot
    except (
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError,
        OSError,
        TypeError,
        ValueError,
    ):
        cache = load_cache() if use_cache_on_error else None
        if all_points(cache):
            return cache

    try:
        snapshot = _http_get_json(config.FALLBACK_DATA_URL)
        if not all_points(snapshot):
            return None
        save_cache(snapshot)
        return snapshot
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None


def all_points(snapshot: dict | None) -> list[dict]:
    """返回公开快照内全部有效的模型档位记录。"""
    if not isinstance(snapshot, dict):
        return []
    points = snapshot.get('points')
    if not isinstance(points, list):
        return []
    return [point for point in points if isinstance(point, dict)]
