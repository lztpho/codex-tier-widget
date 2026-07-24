"""`python -m codex_tier_widget` 入口。

只做两件事：
  1. 检查 Python 版本（必须 ≥ 3.11）
  2. 调用 widget.main() 启动 tkinter 主循环

所有真正的逻辑在 widget.py 里。
"""

from __future__ import annotations

import sys


def main() -> int:
    """启动悬浮窗。返回退出码（0 = 正常退出）。"""
    # Python 版本检查
    if sys.version_info < (3, 11):
        sys.stderr.write(
            '错误：需要 Python 3.11 或更新版本（当前 {}.{}）。\n'
            '请访问 https://www.python.org/downloads/ 下载安装。\n'.format(
                sys.version_info.major, sys.version_info.minor))
        return 1

    try:
        from codex_tier_widget.widget import main as widget_main
    except ImportError as e:
        sys.stderr.write(
            '错误：无法 import widget 模块。\n'
            '原因：{}\n'
            '请确认您是从 src/ 父目录（即含 src/ 的项目根目录）启动，而不是 src/codex_tier_widget/ 内启动。\n'.format(e))
        return 2

    try:
        return widget_main()
    except KeyboardInterrupt:
        # 终端按 Ctrl+C
        return 0


if __name__ == '__main__':
    sys.exit(main())
