"""始终从当前项目源码启动悬浮窗。"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))

from codex_tier_widget.widget import main


if __name__ == '__main__':
    raise SystemExit(main())
