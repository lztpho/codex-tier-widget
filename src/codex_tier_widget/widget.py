"""仅展示三档模型 IQ 与费用的紧凑悬浮窗。"""

from __future__ import annotations

import time
import tkinter as tk
from collections.abc import Callable
from queue import Empty, Queue

from . import config, data
from .autostart import AutoStartManager
from .color import format_iq, format_price, price_color_for, score_for
from .tray import AUTOSTART, EXIT, HIDE, REFRESH, SHOW, TrayController

ROW_HEIGHT = 26
WINDOW_PADDING = 3


class TierRow(tk.Frame):
    """一条不可点击、可拖动的模型信息行。"""

    def __init__(
        self,
        master: tk.Misc,
        *,
        on_drag_start: Callable[[tk.Event], None],
        on_drag: Callable[[tk.Event], None],
    ) -> None:
        super().__init__(
            master,
            height=ROW_HEIGHT,
            bd=0,
            highlightthickness=1,
            takefocus=0,
        )
        self.pack_propagate(False)
        self._on_drag_start = on_drag_start
        self._on_drag = on_drag
        self._captured = False

        self._accent = tk.Frame(self, width=2, bd=0)
        self._model = tk.Label(self, anchor='w', bd=0, font=config.BODY_FONT)
        self._iq = tk.Label(self, anchor='e', bd=0, font=config.SMALL_FONT)
        self._price = tk.Label(self, anchor='e', bd=0, font=config.SMALL_FONT)

        self._accent.place(x=0, y=0, width=2, height=ROW_HEIGHT)
        self._model.place(x=6, y=0, width=90, height=ROW_HEIGHT)
        self._iq.place(x=104, y=0, width=42, height=ROW_HEIGHT)
        self._price.place(x=150, y=0, width=32, height=ROW_HEIGHT)

        for child in (self, self._accent, self._model, self._iq, self._price):
            child.configure(cursor='fleur')
            child.bind('<ButtonPress-1>', self._on_press)
            child.bind('<B1-Motion>', self._on_motion)
            child.bind('<ButtonRelease-1>', self._on_release)

    def update(
        self,
        *,
        label: str,
        iq: float | None,
        price: float | None,
        score: float | None,
    ) -> None:
        self.configure(
            bg=config.ROW_BG,
            highlightbackground=config.ROW_BORDER,
            highlightcolor=config.ROW_BORDER,
        )
        self._accent.configure(bg=price_color_for(score))
        self._model.configure(text=label, fg=config.TEXT_FG, bg=config.ROW_BG)
        self._iq.configure(text=f'IQ{format_iq(iq)}', fg=config.METRIC_FG, bg=config.ROW_BG)
        self._price.configure(
            text=format_price(price),
            fg=price_color_for(score),
            bg=config.ROW_BG,
        )

    def _on_press(self, event: tk.Event) -> None:
        try:
            self.grab_set()
            self._captured = True
        except tk.TclError:
            self._captured = False
        self._on_drag_start(event)

    def _on_motion(self, event: tk.Event) -> None:
        # 纯展示模式下没有点击动作，因此按住后立即跟随，不设置拖动阈值。
        self._on_drag(event)

    def _on_release(self, _event: tk.Event) -> None:
        try:
            if self._captured:
                self.grab_release()
        except tk.TclError:
            pass
        finally:
            self._captured = False


class TierWidget:
    """无标题栏、固定三行的模型数据展示卡片。"""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.snapshot: dict | None = None
        self.last_refresh = 0.0
        self._drag_offset_x = 0
        self._drag_offset_y = 0
        self._closed = False
        self._tray_commands: Queue[str] = Queue()
        self.autostart = AutoStartManager()
        self.autostart.initialize_default_enabled()
        self.tray = TrayController(
            self._tray_commands.put,
            autostart_checked=self.autostart.is_enabled,
            autostart_supported=lambda: self.autostart.supported,
        )

        self._configure_window()
        self.rows: list[TierRow] = []
        self._build_ui()
        self.refresh_data()
        if not self.tray.start():
            error = self.tray.error
            detail = f'（{error}）' if error else ''
            raise RuntimeError(
                f'无法启动系统托盘。请先运行“python -m pip install -r requirements.txt”{detail}'
            )
        self._poll_tray_commands()
        self.tick()

    def _configure_window(self) -> None:
        self.root.title('Codex tiers')
        self.root.overrideredirect(True)
        self.root.configure(bg=config.CARD_BG)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', config.WINDOW_ALPHA)
        self.root.resizable(False, False)
        self.root.bind('<Escape>', lambda _event: self.hide_window())
        self.root.protocol('WM_DELETE_WINDOW', self.hide_window)
        self.root.update_idletasks()

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = max(0, screen_width - config.WINDOW_WIDTH - config.WINDOW_MARGIN)
        y = max(0, screen_height - config.WINDOW_HEIGHT - config.WINDOW_MARGIN)
        self.root.geometry(f'{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}+{x}+{y}')

    def _build_ui(self) -> None:
        content = tk.Frame(self.root, bg=config.CARD_BG, bd=0)
        content.pack(fill='both', expand=True, padx=WINDOW_PADDING, pady=WINDOW_PADDING)
        for _ in range(config.DISPLAY_LIMIT):
            row = TierRow(
                content,
                on_drag_start=self._drag_start,
                on_drag=self._drag_window,
            )
            row.pack(side='top', fill='x')
            self.rows.append(row)

    def _drag_start(self, event: tk.Event) -> None:
        """记录鼠标在窗口中的固定位置，避免增量累积造成拖动脱节。"""
        self.root.update_idletasks()
        self._drag_offset_x = event.x_root - self.root.winfo_rootx()
        self._drag_offset_y = event.y_root - self.root.winfo_rooty()

    def _drag_window(self, _event: tk.Event) -> None:
        """按鼠标的当前绝对位置直接定位窗口。"""
        pointer_x = self.root.winfo_pointerx()
        pointer_y = self.root.winfo_pointery()
        max_x = max(0, self.root.winfo_screenwidth() - config.WINDOW_WIDTH)
        max_y = max(0, self.root.winfo_screenheight() - config.WINDOW_HEIGHT)
        x = max(0, min(pointer_x - self._drag_offset_x, max_x))
        y = max(0, min(pointer_y - self._drag_offset_y, max_y))
        self.root.geometry(f'+{x}+{y}')

    def refresh_data(self) -> None:
        self.last_refresh = time.time()
        self.snapshot = data.fetch_snapshot()
        entries = [(point, score_for(point)) for point in data.all_points(self.snapshot)]

        entries.sort(key=self._rank_key)
        visible_entries = entries[: config.DISPLAY_LIMIT]
        for row, (point, score) in zip(self.rows, visible_entries, strict=False):
            row.update(
                label=self._short_label(point),
                iq=point.get('iq'),
                price=point.get('average_price_usd'),
                score=score,
            )

        for row in self.rows[len(visible_entries) :]:
            row.update(label='—', iq=None, price=None, score=None)

    @staticmethod
    def _short_label(point: dict) -> str:
        """把数据源模型名转换成紧凑显示名称。"""
        model = str(point.get('model') or '').strip().lower()
        for prefix in ('openai.', 'openai/', 'azure.'):
            model = model.removeprefix(prefix)
        model = model.removeprefix('gpt-')
        if not model:
            return '—'

        effort = point.get('effort', point.get('reasoning_effort'))
        if not isinstance(effort, str) or not effort.strip():
            return model or '—'
        return f'{model}-{effort.strip().lower().replace("_", "-")}'

    @staticmethod
    def _rank_key(entry: tuple[dict, float | None]) -> tuple[float, ...]:
        """先保证 IQ 达标，再比较 IQ 与费用的性价比。"""
        point, score = entry

        iq = point.get('iq')
        price = point.get('average_price_usd')
        if not isinstance(iq, (int, float)) or score is None:
            return (2.0, float('inf'), 0.0)
        if not isinstance(price, (int, float)) or price <= 0:
            price = float('inf')

        group = 0.0 if iq >= config.MINIMUM_IQ else 1.0
        return (group, -score, float(price))

    def tick(self) -> None:
        if time.time() - self.last_refresh >= config.REFRESH_SECONDS:
            self.refresh_data()
        self.root.after(60_000, self.tick)

    def _poll_tray_commands(self) -> None:
        while True:
            try:
                command = self._tray_commands.get_nowait()
            except Empty:
                break

            if command == SHOW:
                self.show_window()
            elif command == HIDE:
                self.hide_window()
            elif command == REFRESH:
                self.refresh_data()
            elif command == AUTOSTART:
                self.autostart.toggle()
                self.tray.refresh_menu()
            elif command == EXIT:
                self.close()

        if not self._closed:
            self.root.after(100, self._poll_tray_commands)

    def show_window(self) -> None:
        """显示并激活悬浮窗。"""
        if self._closed:
            return
        self.root.deiconify()
        self.root.lift()
        self.root.attributes('-topmost', True)

    def hide_window(self) -> None:
        """隐藏悬浮窗，但保持程序与托盘图标运行。"""
        if not self._closed:
            self.root.withdraw()

    def close(self) -> None:
        """从托盘退出程序，并清理托盘图标。"""
        if self._closed:
            return
        self._closed = True
        self.tray.stop()
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def mainloop(self) -> None:
        self.root.mainloop()


def main() -> int:
    widget: TierWidget | None = None
    try:
        widget = TierWidget()
        widget.mainloop()
    except RuntimeError as exc:
        print(f'启动失败：{exc}')
        return 1
    except KeyboardInterrupt:
        return 0
    finally:
        if widget is not None:
            widget.close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
