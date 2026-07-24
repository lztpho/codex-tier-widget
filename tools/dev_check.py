#!/usr/bin/env python3
"""开发者脚本：手动跑与 CI 等价的所有静态检查 + 烟雾测试。

用法：
    python tools/dev_check.py         # 跑所有
    python tools/dev_check.py syntax  # 只跑语法检查
    python tools/dev_check.py lint    # 只跑 lint
    python tools/dev_check.py smoke   # 只跑 import smoke + color smoke
    python tools/dev_check.py all     # 全跑（默认）

退出码：0 = 通过；非 0 = 失败。
"""

from __future__ import annotations

import compileall
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / 'src'


def syntax_check() -> int:
    """compileall 语法检查。"""
    print('🔍 Syntax check (python -m compileall)...')
    ok = compileall.compile_dir(
        str(SRC), quiet=1, force=True,
    )
    if ok:
        print('  ✓ OK')
    return 0 if ok else 1


def lint_check() -> int:
    """ruff + pyflakes（如果装了）。"""
    rc = 0
    for tool in ('ruff', 'pyflakes'):
        try:
            print(f'🔍 {tool}...')
            r = subprocess.run(
                [sys.executable, '-m', tool, 'check', str(SRC)]
                if tool == 'ruff' else
                [sys.executable, '-m', tool, str(SRC)],
                capture_output=True, text=True,
            )
            if r.returncode == 0:
                print(f'  ✓ {tool} OK')
            else:
                print(f'  ✗ {tool} FAILED:')
                print(r.stdout)
                print(r.stderr)
                rc = 1
        except FileNotFoundError:
            print(f'  ⚠ {tool} not installed, skipping')
    return rc


def smoke_import() -> int:
    """import smoke test：所有模块能导入且不抛错。"""
    print('🔍 Import smoke test...')
    # 把 src 加到 sys.path 以便 import
    sys.path.insert(0, str(SRC))
    try:
        import codex_tier_widget  # noqa: F401
        from codex_tier_widget import color, codex_config, config, data  # noqa: F401
        # widget import 会拉动 tkinter (可能未装)，try 一下
        try:
            from codex_tier_widget import widget  # noqa: F401
            print('  ✓ widget imported (tkinter available)')
        except ImportError as e:
            print(f'  ⚠ widget not imported: {e} (likely missing tkinter on headless)')
    except Exception as e:
        print(f'  ✗ import FAILED: {e}')
        return 1
    print('  ✓ OK')
    return 0


def smoke_color() -> int:
    """color.py 关键路径。"""
    print('🔍 Color smoke test...')
    sys.path.insert(0, str(SRC))
    from codex_tier_widget.color import color_for, format_iq, format_price, score_for

    cases = [
        # (score, expected_fg_starts_with)
        (60, '#'),  # 极绿
        (40, '#'),  # 纯绿
        (25, '#'),  # 黄绿
        (15, '#'),  # 橙黄
        (3,  '#'),  # 红
        (None, '#'),  # 灰
    ]
    for score, prefix in cases:
        fg, bg = color_for(score)
        assert fg.startswith(prefix), f'fg should be hex: {fg}'
        assert bg.startswith(prefix), f'bg should be hex: {bg}'

    # score_for 边界
    assert score_for(None) is None
    assert score_for({}) is None
    assert score_for({'iq': 0, 'average_price_usd': 1.0}) is None
    assert score_for({'iq': 90, 'average_price_usd': 0}) is None
    s = score_for({'iq': 90, 'average_price_usd': 3.0})
    assert abs(s - 30) < 1e-6, f'expected 30, got {s}'

    # format_iq / format_price
    assert format_iq(None) == '—'
    assert format_iq(100) == '100'
    assert format_iq(89.7) == '89.7'
    assert format_price(None) == '—'
    assert format_price(1.63) == '$1.63'

    print('  ✓ OK')
    return 0


def smoke_codex_config_roundtrip() -> int:
    """codex_config.py 读写 round-trip（用临时目录）。"""
    print('🔍 CodexConfig round-trip test...')
    import tempfile
    sys.path.insert(0, str(SRC))
    from codex_tier_widget.codex_config import CodexConfig

    with tempfile.TemporaryDirectory() as tmp:
        cfg_dir = Path(tmp) / '.codex'
        cfg_dir.mkdir()
        cfg_path = cfg_dir / 'config.toml'
        cfg_path.write_text(
            'model = "gpt-5-codex"\n'
            'model_reasoning_effort = "high"\n'
            'other_field = "preserve me"\n',
            encoding='utf-8',
        )
        cfg = CodexConfig(path=cfg_path)
        state = cfg.read()
        assert state == {'model': 'gpt-5-codex', 'effort': 'high'}, f'unexpected: {state}'

        # write
        assert cfg.write('gpt-5-codex', 'xhigh') is True
        text = cfg_path.read_text(encoding='utf-8')
        assert 'model_reasoning_effort = "xhigh"' in text
        assert 'other_field = "preserve me"' in text, '其他字段必须保留'

        # mtime 探测
        assert cfg.mtime() > 0
        cfg.last_mtime = cfg.mtime()
        assert cfg.changed() is False
        time.sleep(0.05)
        cfg.last_mtime -= 1
        assert cfg.changed() is True

    print('  ✓ OK')
    return 0


COMMANDS = {
    'syntax': syntax_check,
    'lint':   lint_check,
    'smoke':  lambda: (smoke_import() + smoke_color() + smoke_codex_config_roundtrip()),
    'all':    lambda: (syntax_check() + lint_check() + smoke_import() + smoke_color() + smoke_codex_config_roundtrip()),
}


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] not in COMMANDS:
        print(__doc__)
        print(f"可用子命令: {', '.join(COMMANDS.keys())}")
        return 2 if len(argv) >= 2 else 0
    return COMMANDS[argv[1]]()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
