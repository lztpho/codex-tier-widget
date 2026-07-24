"""codex_tier_widget — 静态配置。

所有用户可改的配置都集中在这里：
  - TIERS            三档推荐（普通 / 中等 / 高级）
  - MODEL_ALIAS      Codex CLI model 字符串 → codexradar 档案 model 名 映射
  - COLOR_THRESHOLDS 性价比 → (前景, 背景) 颜色的绝对阈值表
  - 其他运行时参数（数据源 URL、刷新间隔、轮询周期、Codex 配置路径）

改完这里重启 widget.py 即生效，无需改其他文件。

更多说明：[USAGE.md § 2](../../USAGE.md)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# 三档推荐
# ─────────────────────────────────────────────────────────────────────────────
# 名称 / codexradar 模型 / 推理强度 / 一句话提示
# 按用户的「更省钱」策略挑选，覆盖日常编码 → 复杂任务的 95% 场景
TIERS: list[dict] = [
    {
        'name':   '普通档',
        'model':  'gpt-5.6-luna',
        'effort': 'xhigh',
        'tip':    '日常编码、调试、单文件 < 300 行',
    },
    {
        'name':   '中等档',
        'model':  'gpt-5.6-terra',
        'effort': 'xhigh',
        'tip':    '跨文件改造、FOC 控制环、中断逻辑',
    },
    {
        'name':   '高级档',
        'model':  'gpt-5.6-sol',
        'effort': 'medium',
        'tip':    '架构设计、debug 难题、模糊需求分析',
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# 模型名映射表
# ─────────────────────────────────────────────────────────────────────────────
# Codex CLI 配置里的 model 字段是 OpenAI 真实 ID（"gpt-5-codex" / "gpt-5"），
# codexradar 用的是订阅档名（"gpt-5.6-sol" / "gpt-5.6-terra" / "gpt-5.6-luna"）。
# 两套命名空间不一一对应——这里维护映射关系，用户实测后可改。
#
# 探测到的 model 不在表里 → 当前档显示「未知档」并提示改这里。
MODEL_ALIAS: dict[str, str | None] = {
    # Codex CLI 字符串    →  codexradar 档案 model 名
    'gpt-5-codex':        'gpt-5.6-sol',
    'gpt-5':              'gpt-5.6-sol',
    'gpt-5-mini':         'gpt-5.6-luna',
    'gpt-5-nano':         'gpt-5.6-luna',
}

# ─────────────────────────────────────────────────────────────────────────────
# 颜色绝对阈值（性价比 → 颜色）
# ─────────────────────────────────────────────────────────────────────────────
# 性价比 = IQ / price (USD per 1M token)
# 选择绝对阈值（不用 min-max）是为了：3 推荐档全部稳定在绿色系，
# 只有「选贵了」才明显变黄/红，眼睛一扫就知道是不是选错了。
#
# 阈值用户可改：(threshold_min, 前景色, 背景色)
COLOR_THRESHOLDS: list[tuple[float, str, str]] = [
    (50, '#0e8c5b', '#d1f5ea'),  # ≥50  极绿（teal-green）
    (30, '#1e8449', '#daf5e3'),  # 30~50 纯绿
    (20, '#82c272', '#e8f5d8'),  # 20~30 黄绿
    (10, '#f39c12', '#fde9d4'),  # 10~20 橙黄
    (5,  '#e67e22', '#fce4cf'),  # 5~10  橙红
    (0,  '#c0392b', '#fadbd8'),  # <5    红（"血亏"）
]

GRAY_FG = '#666666'
GRAY_BG = '#e8e8e8'

# 选中徽章颜色（"正在使用" 标记的内框）
SELECTED_FG = '#1a1a1a'
SELECTED_BG = '#fffbe6'  # 浅米色高亮

# ─────────────────────────────────────────────────────────────────────────────
# 数据源
# ─────────────────────────────────────────────────────────────────────────────
# codexradar 的实时 IQ 跑测快照端点（参见 docs/ARCHITECTURE.md § 2.1）
DATA_URL = (
    'https://codexradar.com/data/intelligence-efficiency.json'
    '?v=20260723-0710-history-metrics'
)
DATA_CACHE = Path.home() / '.codex_radar_cache.json'

# 数据刷新间隔（秒）
REFRESH_SECONDS = 600  # 10 分钟，与 codexradar 自身的刷新周期同步

# Codex config.toml mtime 轮询间隔（毫秒）—— 用户手动切换的感知延迟
POLL_INTERVAL_MS = 2000

# HTTP 请求超时（秒）：connect, read
HTTP_TIMEOUT = (3, 5)

# ─────────────────────────────────────────────────────────────────────────────
# Codex CLI 配置文件路径
# ─────────────────────────────────────────────────────────────────────────────
# Windows: %USERPROFILE%\.codex\config.toml
# macOS / Linux: ~/.codex/config.toml
def codex_config_path() -> Path:
    """返回当前平台的 Codex 配置文件路径。"""
    if sys.platform == 'win32':
        base = Path(os.environ.get('USERPROFILE') or str(Path.home()))
    else:
        base = Path.home()
    return base / '.codex' / 'config.toml'

# ─────────────────────────────────────────────────────────────────────────────
# 窗口外观
# ─────────────────────────────────────────────────────────────────────────────
WINDOW_WIDTH   = 320
WINDOW_HEIGHT  = 230
WINDOW_ALPHA   = 0.92   # 半透背景
WINDOW_MARGIN  = 24     # 距离屏幕右下角的边距 (px)

# 字体（用微软雅黑，跨平台 fallback 到默认 sans-serif）
TITLE_FONT = ('Microsoft YaHei UI', 9, 'bold')
BODY_FONT  = ('Microsoft YaHei UI', 9)
SMALL_FONT = ('Microsoft YaHei UI', 8)
BUTTON_FONT = ('Microsoft YaHei UI', 8, 'bold')
