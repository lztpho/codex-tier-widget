"""系统托盘图标与后台命令队列。"""

from __future__ import annotations

import threading
from collections.abc import Callable

SHOW = 'show'
HIDE = 'hide'
REFRESH = 'refresh'
AUTOSTART = 'autostart'
EXIT = 'exit'


class TrayController:
    """在独立线程运行系统托盘，并把菜单操作交给 Tk 主线程处理。"""

    def __init__(
        self,
        command_sink: Callable[[str], None],
        *,
        autostart_checked: Callable[[], bool],
        autostart_supported: Callable[[], bool],
    ) -> None:
        self._command_sink = command_sink
        self._autostart_checked = autostart_checked
        self._autostart_supported = autostart_supported
        self._icon = None
        self._thread: threading.Thread | None = None
        self._ready = threading.Event()
        self._error: Exception | None = None

    @property
    def error(self) -> Exception | None:
        """返回托盘初始化错误。"""
        return self._error

    def start(self) -> bool:
        """启动托盘线程；依赖缺失或初始化失败时返回 False。"""
        try:
            from importlib.util import find_spec

            if find_spec('pystray') is None:
                raise ModuleNotFoundError('缺少 pystray')
            if find_spec('PIL') is None:
                raise ModuleNotFoundError('缺少 Pillow')
        except ImportError as exc:
            self._error = exc
            return False

        self._thread = threading.Thread(
            target=self._run,
            name='codex-tier-tray',
            daemon=True,
        )
        self._thread.start()
        self._ready.wait(timeout=3.0)
        return self._icon is not None and self._error is None

    def stop(self) -> None:
        """移除托盘图标并等待托盘线程结束。"""
        if self._icon is not None:
            try:
                self._icon.stop()
            except (OSError, RuntimeError) as exc:
                self._error = self._error or exc
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=3.0)

    def refresh_menu(self) -> None:
        """刷新托盘菜单中的动态勾选状态。"""
        if self._icon is not None:
            try:
                self._icon.update_menu()
            except (OSError, RuntimeError) as exc:
                self._error = self._error or exc

    def _run(self) -> None:
        try:
            import pystray

            self._icon = pystray.Icon(
                'codex-tier-widget',
                self._create_image(),
                'Codex 档位',
                pystray.Menu(
                    pystray.MenuItem(
                        '显示悬浮窗',
                        lambda _icon, _item: self._send(SHOW),
                        default=True,
                    ),
                    pystray.MenuItem(
                        '隐藏悬浮窗',
                        lambda _icon, _item: self._send(HIDE),
                    ),
                    pystray.MenuItem(
                        '立即刷新',
                        lambda _icon, _item: self._send(REFRESH),
                    ),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem(
                        '开机自启',
                        lambda _icon, _item: self._send(AUTOSTART),
                        checked=lambda _item: self._autostart_checked(),
                        enabled=lambda _item: self._autostart_supported(),
                    ),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem(
                        '退出程序',
                        lambda _icon, _item: self._send(EXIT),
                    ),
                ),
            )
            self._ready.set()
            self._icon.run()
        except (ImportError, OSError, RuntimeError) as exc:
            self._error = exc
            self._ready.set()

    def _send(self, command: str) -> None:
        """把托盘菜单命令送回 Tk 主线程。"""
        self._command_sink(command)

    @staticmethod
    def _create_image():
        """绘制一个不依赖外部图片文件的托盘图标。"""
        from PIL import Image, ImageDraw

        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle(
            (3, 3, 61, 61),
            radius=12,
            fill='#151a21',
            outline='#74d6aa',
            width=3,
        )
        draw.line((15, 20, 49, 20), fill='#74d6aa', width=5)
        draw.line((15, 32, 43, 32), fill='#d2dc80', width=5)
        draw.line((15, 44, 37, 44), fill='#f2c46d', width=5)
        return image
