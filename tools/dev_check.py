#!/usr/bin/env python3
"""本地开发检查。

用法：
    python tools/dev_check.py syntax
    python tools/dev_check.py smoke
    python tools/dev_check.py all
"""

from __future__ import annotations

import compileall
import sys
from importlib import import_module
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src'


def syntax_check() -> int:
    """编译全部源码，检查语法。"""
    ok = compileall.compile_dir(str(SRC), quiet=1, force=True)
    print('语法检查通过' if ok else '语法检查失败')
    return 0 if ok else 1


def smoke_import() -> int:
    """确认纯展示组件的模块都能导入。"""
    sys.path.insert(0, str(SRC))
    try:
        for module in (
            'codex_tier_widget',
            'codex_tier_widget.autostart',
            'codex_tier_widget.color',
            'codex_tier_widget.config',
            'codex_tier_widget.data',
            'codex_tier_widget.tray',
            'codex_tier_widget.widget',
        ):
            import_module(module)
    except (ImportError, OSError, RuntimeError) as exc:
        print(f'导入检查失败：{exc}')
        return 1
    print('导入检查通过')
    return 0


def smoke_color() -> int:
    """验证显示格式和性价比分数的基本行为。"""
    sys.path.insert(0, str(SRC))
    from codex_tier_widget.color import format_iq, format_price, price_color_for, score_for

    assert score_for(None) is None
    assert score_for({'iq': 90, 'average_price_usd': 3.0}) == 30
    assert format_iq(None) == '—'
    assert format_iq(89.7) == '89.7'
    assert format_price(None) == '—'
    assert format_price(1.63) == '$1.63'
    assert price_color_for(30).startswith('#')
    print('数据格式检查通过')
    return 0


COMMANDS = {
    'syntax': syntax_check,
    'smoke': lambda: smoke_import() + smoke_color(),
    'all': lambda: syntax_check() + smoke_import() + smoke_color(),
}


def main(argv: list[str]) -> int:
    command = argv[1] if len(argv) > 1 else 'all'
    if command not in COMMANDS:
        print(f'可用命令：{", ".join(COMMANDS)}')
        return 2
    return COMMANDS[command]()


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
