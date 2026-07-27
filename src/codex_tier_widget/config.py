"""悬浮窗的静态配置。"""

from __future__ import annotations

from pathlib import Path

# 每次刷新从全部公开数据中重算，只显示排名前三的档位。
DISPLAY_LIMIT = 3

# 数据源与刷新策略。主接口与 Codex 雷达网页使用同一份实时任务表；
# 旧快照只在首次启动且主接口不可用时兜底。
DATA_URL = 'https://api.codexradar.com/api/v1/table'
FALLBACK_DATA_URL = 'https://codexradar.com/data/intelligence-efficiency.json'
DATA_CACHE = Path.home() / '.codex_radar_cache.json'
REFRESH_SECONDS = 600
HTTP_TIMEOUT = 5.0
MINIMUM_IQ = 80.0

# 窗口尺寸与深色卡片配色。
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
