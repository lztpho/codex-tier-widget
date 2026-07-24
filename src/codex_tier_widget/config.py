"""悬浮窗的静态展示配置。"""

from __future__ import annotations

from pathlib import Path


# 三个固定展示档位。effort 与界面名称保持一致，用于匹配公开数据。
TIERS: list[dict[str, str]] = [
    {'label': '5.6-luna-max', 'model': 'gpt-5.6-luna', 'effort': 'max'},
    {'label': '5.6-terra-max', 'model': 'gpt-5.6-terra', 'effort': 'max'},
    {'label': '5.6-sol-medium', 'model': 'gpt-5.6-sol', 'effort': 'medium'},
]


# 保留数据格式化和开发自检所需的性价比颜色阈值。
COLOR_THRESHOLDS: list[tuple[float, str, str]] = [
    (50, '#0e8c5b', '#d1f5ea'),
    (30, '#1e8449', '#daf5e3'),
    (20, '#82c272', '#e8f5d8'),
    (10, '#f39c12', '#fde9d4'),
    (5, '#e67e22', '#fce4cf'),
    (0, '#c0392b', '#fadbd8'),
]

GRAY_FG = '#666666'
GRAY_BG = '#e8e8e8'


DATA_URL = 'https://codexradar.com/data/intelligence-efficiency.json'
DATA_CACHE = Path.home() / '.codex_radar_cache.json'
REFRESH_SECONDS = 600
HTTP_TIMEOUT = 5.0
# 排名门槛：达到该 IQ 后，再按 IQ ÷ 费用的性价比排序。
MINIMUM_IQ = 80.0


# 窗口尺寸和深色卡片配色。
WINDOW_WIDTH = 190
WINDOW_HEIGHT = 84
WINDOW_ALPHA = 0.98
WINDOW_MARGIN = 12

BODY_FONT = ('Microsoft YaHei UI', 8)
SMALL_FONT = ('Microsoft YaHei UI', 8)

CARD_BG = '#151a21'
ROW_BG = '#1d242d'
ROW_BORDER = '#2b3642'
TEXT_FG = '#f2f5f8'
METRIC_FG = '#aeb9c5'
MUTED_FG = '#697583'
PRICE_GOOD_FG = '#74d6aa'
PRICE_MID_FG = '#d2dc80'
PRICE_WARN_FG = '#f2c46d'
PRICE_BAD_FG = '#ef8f8f'
