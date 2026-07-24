"""codex_tier_widget.widget — tkinter 主程序。

布局：
    ┌─ 状态行 ─────────────────────────────────┐
    │ Codex 档位 · 21:34    ●实时连动             │
    ├─ TierRow (普通档) ──────────────────────┤
    │ 🟢 普通档                                  │
    │   luna xhigh   IQ 84.4                     │
    │   $1.63/次     [ 使用此档 ]                │
    ├─ TierRow (中等档) ──────────────────────┤
    │ ...                                        │
    ├─ TierRow (高级档) ──────────────────────┤
    │ ...                                        │
    ├─ CurrentRow (当前档, 默认隐藏) ─────────┤
    │ ⚙️ 当前档（你正在用 Codex）                │
    │   gpt-5-codex high  IQ 87.1               │
    │   $5.87/次                                  │
    ├─ 底栏 ───────────────────────────────────┤
    │ ↻ 刷新         选中: ●普通档              │
    └──────────────────────────────────────────┘

主循环：
    tick() 每 2 秒执行：
      1. 检测 ~/.codex/config.toml mtime → 变了 → 重渲第 4 档
      2. 距上次拉数据 > REFRESH_SECONDS → 重拉 codexradar → 重算染色
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox
from typing import Any, Callable

from . import config, data
from .codex_config import CodexConfig
from .color import color_for, format_iq, format_price, score_for


# ════════════════════════════════════════════════════════════════════════════
# 单档行（推荐档 / 当前档 共用骨架）
# ════════════════════════════════════════════════════════════════════════════


class TierRow(tk.Frame):
    """一行 tier UI：标签 + IQ + 价格 + 按钮。

    作为基类，被 TierRowRecommended（带"使用此档"按钮）和 TierRowCurrent
    （只读，反映用户在用的档）继承/复用。
    """

    PADDING_X = 8
    PADDING_Y = 4

    def __init__(self, master: tk.Misc, *, title: str, on_use: Callable[[], None] | None = None) -> None:
        super().__init__(master, bd=0, highlightthickness=1, highlightbackground='#cccccc')
        self._title = title
        self._on_use = on_use
        self._build()

    # ── 布局 ──────────────────────────────────────────────────────────────

    def _build(self) -> None:
        # 上行：emoji + 档名（如「🟢 普通档」）
        self._title_lbl = tk.Label(
            self, text='', anchor='w',
            font=config.TITLE_FONT, padx=self.PADDING_X, pady=2,
        )
        self._title_lbl.pack(side='top', fill='x')

        # 中行：model + effort (左) + IQ (右)
        body = tk.Frame(self, bd=0)
        body.pack(side='top', fill='x')

        self._model_lbl = tk.Label(
            body, text='', anchor='w',
            font=config.BODY_FONT, padx=self.PADDING_X,
        )
        self._model_lbl.pack(side='left')

        self._iq_lbl = tk.Label(
            body, text='', anchor='e',
            font=config.BODY_FONT, padx=self.PADDING_X,
        )
        self._iq_lbl.pack(side='right')

        # 下行：价格 (左) + 按钮 (右)
        bottom = tk.Frame(self, bd=0)
        bottom.pack(side='top', fill='x')

        self._price_lbl = tk.Label(
            bottom, text='', anchor='w',
            font=config.SMALL_FONT, padx=self.PADDING_X, pady=2,
        )
        self._price_lbl.pack(side='left')

        if self._on_use is not None:
            self._btn = tk.Button(
                bottom, text='使用此档',
                font=config.BUTTON_FONT,
                bd=1, relief='ridge', padx=8, pady=1,
                command=self._on_use,
            )
            self._btn.pack(side='right', padx=self.PADDING_X)

    # ── 暴露给外部的更新方法 ──────────────────────────────────────────────

    def update_content(
        self,
        *,
        title: str,
        model: str,
        effort: str,
        point: dict | None,
        selected: bool = False,
        tip: str = '',
    ) -> None:
        """更新本行显示。"""
        score = score_for(point)
        fg, bg = color_for(score)

        self._title_lbl.configure(text=title, fg=fg, bg=bg)
        self._model_lbl.configure(text=f'{model} {effort}', fg=fg, bg=bg)
        self._iq_lbl.configure(text=f'IQ {format_iq(point.get("iq") if point else None)}', fg=fg, bg=bg)
        self._price_lbl.configure(text=f'{format_price(point.get("average_price_usd") if point else None)}/次', fg=fg, bg=bg)

        # 整行 frame 用背景色（更明显的视觉块）
        self.configure(bg=bg)
        for child in self.winfo_children():
            child.configure(bg=bg)

        if selected:
            self.configure(highlightbackground=config.SELECTED_FG, highlightthickness=2)
        else:
            self.configure(highlightbackground='#cccccc', highlightthickness=1)

        if tip:
            self._title_lbl.configure(text=f'{title}  · {tip}', fg=fg, bg=bg)

    def set_unknown(self, *, codex_model: str, effort: str) -> None:
        """当前档探到，但 model 不在 MODEL_ALIAS 里（未知档）。"""
        fg, bg = color_for(None)  # 灰色
        self._title_lbl.configure(text='⚙️ 当前档（未知档 ⓘ）', fg=fg, bg=bg)
        self._model_lbl.configure(text=f'{codex_model} {effort}', fg=fg, bg=bg)
        self._iq_lbl.configure(text='IQ —', fg=fg, bg=bg)
        self._price_lbl.configure(text='未在 MODEL_ALIAS 中映射', fg=fg, bg=bg)
        self.configure(bg=bg)
        for child in self.winfo_children():
            child.configure(bg=bg)

    def clear(self) -> None:
        """清空（用于 hide() 之前）。"""
        for lbl in (self._title_lbl, self._model_lbl, self._iq_lbl, self._price_lbl):
            lbl.configure(text='')


# ════════════════════════════════════════════════════════════════════════════
# 主窗口
# ════════════════════════════════════════════════════════════════════════════


class TierWidget:
    """主窗口管理：UI 构建、tick 调度、用户交互。"""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self._configure_window()

        self.codex = CodexConfig()
        self.snapshot: dict | None = None
        self.last_refresh: float = 0.0   # epoch seconds
        self.selected: dict | None = None  # 当前 Codex 在用的 (model_aliased, effort)

        # 4 行（最后一个默认隐藏）
        self.recommended_rows: list[TierRow] = []
        self.current_row: TierRow | None = None

        self._build_ui()
        self._install_drag(self.root)

        # 启动后立刻拉一次数据，让用户看到的是真实数据
        self.refresh_data()
        # 触发一次当前档探测
        self._refresh_current_tier()

        # 启动 tick 循环
        self.tick()

    # ── 窗口配置 ──────────────────────────────────────────────────────────

    def _configure_window(self) -> None:
        """frameless + 半透 + 始终置顶 + 右下角定位。"""
        self.root.title('Codex Tier Widget')
        self.root.overrideredirect(True)  # 无标题栏
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', config.WINDOW_ALPHA)

        # 定位：主屏右下角
        self.root.update_idletasks()  # 让 winfo_screenwidth 拿到真实值
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = max(0, sw - config.WINDOW_WIDTH - config.WINDOW_MARGIN)
        y = max(0, sh - config.WINDOW_HEIGHT - config.WINDOW_MARGIN - 40)  # 40 任务栏
        self.root.geometry(f'{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}+{x}+{y}')
        self.root.minsize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.root.maxsize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

    # ── UI 构建 ──────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # 顶部状态行
        self.status_lbl = tk.Label(
            self.root,
            text='Codex 档位 · --:--',
            anchor='w',
            font=config.SMALL_FONT,
            padx=10, pady=4,
            bg='#f5f5f5', fg='#333333',
        )
        self.status_lbl.pack(side='top', fill='x')

        # 3 个推荐档
        for tier in config.TIERS:
            row = TierRow(
                self.root,
                title=f'{_tier_emoji(tier["name"])} {tier["name"]}',
                on_use=(lambda t=tier: self._use_recommended(t)),
            )
            row.pack(side='top', fill='x', padx=0, pady=2)
            self.recommended_rows.append(row)

        # 分割线
        sep = tk.Frame(self.root, height=1, bg='#dddddd')
        sep.pack(side='top', fill='x', padx=4)

        # 第 4 档：当前档（默认 pack 但 grid_remove，之后按需 show/hide）
        self.current_row = TierRow(
            self.root,
            title='⚙️ 当前档',
            on_use=None,
        )
        self.current_row.pack(side='top', fill='x', padx=0, pady=2)
        self.current_row.pack_forget()  # 先隐藏

        # 底栏
        bottom = tk.Frame(self.root, bd=0, bg='#f5f5f5')
        bottom.pack(side='top', fill='x')

        self.refresh_btn = tk.Button(
            bottom, text='↻ 刷新',
            font=config.SMALL_FONT,
            bd=1, relief='ridge', padx=6, pady=1,
            command=self.refresh_data,
        )
        self.refresh_btn.pack(side='left', padx=8, pady=2)

        self.selected_lbl = tk.Label(
            bottom, text='选中: —',
            anchor='e', font=config.SMALL_FONT,
            padx=10, pady=2, bg='#f5f5f5', fg='#333333',
        )
        self.selected_lbl.pack(side='right', fill='x', expand=True)

        # 状态行更新
        self._update_status_line()

    # ── 拖动支持 ──────────────────────────────────────────────────────────

    def _install_drag(self, widget: tk.Misc) -> None:
        """鼠标按住顶部拖动整个窗口。"""
        widget.bind('<Button-1>', self._on_drag_start)
        widget.bind('<B1-Motion>', self._on_drag_move)
        widget.bind('<ButtonRelease-1>', self._on_drag_end)
        # 给状态行单独绑定（用户拖的入口）
        self.status_lbl.bind('<Button-1>', self._on_drag_start)
        self.status_lbl.bind('<B1-Motion>', self._on_drag_move)
        self.status_lbl.bind('<ButtonRelease-1>', self._on_drag_end)

    def _on_drag_start(self, event: tk.Event) -> None:
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag_move(self, event: tk.Event) -> None:
        x = self.root.winfo_x() + event.x - self._drag_x
        y = self.root.winfo_y() + event.y - self._drag_y
        self.root.geometry(f'+{x}+{y}')

    def _on_drag_end(self, event: tk.Event) -> None:
        pass

    # ── 数据刷新 ──────────────────────────────────────────────────────────

    def refresh_data(self) -> None:
        """拉 codexradar JSON，更新所有可见行，重新染色。"""
        self.last_refresh = time.time()
        self.snapshot = data.fetch_snapshot()

        # 推荐档：永远更新（即使没数据也显示「—」）
        for idx, tier in enumerate(config.TIERS):
            point = data.find_point(self.snapshot, tier['model'], tier['effort'])
            self.recommended_rows[idx].update_content(
                title=f'{_tier_emoji(tier["name"])} {tier["name"]}',
                model=tier['model'],
                effort=tier['effort'],
                point=point,
                selected=self._is_recommended_selected(tier),
                tip=tier.get('tip', ''),
            )

        # 第 4 档：也要根据新数据重绘
        self._refresh_current_tier()
        self._update_status_line()

    def _is_recommended_selected(self, tier: dict) -> bool:
        """用户当前选中的模型是不是这个 tier？"""
        return self.selected is not None \
            and self.selected['model'] == tier['model'] \
            and self.selected['effort'] == tier['effort']

    def _refresh_current_tier(self) -> None:
        """重新读 ~/.codex/config.toml，更新第 4 档或隐藏它。"""
        if self.current_row is None:
            return
        codex_state = self.codex.read()
        if codex_state is None or not codex_state.get('model'):
            self.current_row.pack_forget()
            self.selected = None
            self.selected_lbl.configure(text='选中: —')
            return

        # 通过 MODEL_ALIAS 映射到 codexradar 名
        codex_model = codex_state['model']
        codex_effort = codex_state.get('effort') or ''
        aliased = config.MODEL_ALIAS.get(codex_model)
        if aliased is None:
            # 用户用的 model 不在 alias 里 → 第 4 档显示未知档 + 提示
            self.current_row.update_content(
                title='⚙️ 当前档（未知档 ⓘ）',
                model=codex_model, effort=codex_effort,
                point=None,
                selected=False,
            )
            self.current_row.pack(side='top', fill='x', padx=0, pady=2)
            self.selected = {'model': codex_model, 'effort': codex_effort}  # 用原名
            self.selected_lbl.configure(text='选中: ⚠ 未知档')
            return

        # 检查是否跟某个推荐档相同
        for idx, tier in enumerate(config.TIERS):
            if aliased == tier['model'] and codex_effort == tier['effort']:
                # 是推荐档之一 → 整行隐藏
                self.current_row.pack_forget()
                self.selected = {'model': aliased, 'effort': codex_effort}
                # 同步给对应推荐档加「选中」徽章
                for j, t in enumerate(config.TIERS):
                    point = data.find_point(self.snapshot, t['model'], t['effort'])
                    self.recommended_rows[j].update_content(
                        title=f'{_tier_emoji(t["name"])} {t["name"]}',
                        model=t['model'], effort=t['effort'],
                        point=point,
                        selected=(j == idx),
                        tip=t.get('tip', ''),
                    )
                self.selected_lbl.configure(
                    text=f'选中: ●{tier["name"]}'
                )
                return

        # 不是推荐档 → 显示第 4 档
        point = data.find_point(self.snapshot, aliased, codex_effort)
        self.current_row.update_content(
            title='⚙️ 当前档',
            model=aliased, effort=codex_effort,
            point=point,
            selected=False,
        )
        self.current_row.pack(side='top', fill='x', padx=0, pady=2)
        self.selected = {'model': aliased, 'effort': codex_effort}
        self.selected_lbl.configure(text='选中: ⚙ 当前档')

    def _update_status_line(self) -> None:
        """顶部状态行：当前时间 + 数据新鲜度（相对时间）。"""
        ts = data.current_time_text()
        upd = data.updated_relative_text(self.snapshot)
        self.status_lbl.configure(text=f'Codex 档位 · {ts}    {upd}')

    # ── 用户操作 ──────────────────────────────────────────────────────────

    def _use_recommended(self, tier: dict) -> None:
        """按「使用此档」按钮的回调。"""
        msg = (
            f'确认将 Codex 切换到：\n\n'
            f'  Model: {tier["model"]}\n'
            f'  Effort: {tier["effort"]}\n\n'
            f'（Codex CLI 重启后生效）'
        )
        if not messagebox.askyesno('切换 Codex 档位', msg, parent=self.root):
            return

        ok = self.codex.write(tier['model'], tier['effort'])
        if ok:
            self.status_lbl.configure(text='●已写入 config.toml，请重启 Codex 生效')
            # 立即更新 last_mtime 触发后续 tick 看到新状态
            self.codex.last_mtime = self.codex.mtime()
            self._refresh_current_tier()
        else:
            messagebox.showerror(
                '写入失败',
                '无法写入 ~/.codex/config.toml。请检查：\n'
                '  1. 文件存在\n'
                '  2. 当前用户有写权限\n'
                '  3. Codex CLI 没在占用文件',
                parent=self.root,
            )

    # ── tick 循环 ─────────────────────────────────────────────────────────

    def tick(self) -> None:
        """每 POLL_INTERVAL_MS 毫秒调度一次。"""
        # 1) 探测 config.toml mtime 变化
        if self.codex.changed() and self.codex.last_mtime > 0:
            self._refresh_current_tier()

        # 2) 数据刷新周期
        now = time.time()
        if now - self.last_refresh >= config.REFRESH_SECONDS:
            self.refresh_data()

        # 3) 每分钟更新状态行的时间显示
        self._update_status_line()

        # 4) 注册下次回调
        self.root.after(config.POLL_INTERVAL_MS, self.tick)

    # ── 主循环入口 ────────────────────────────────────────────────────────

    def mainloop(self) -> None:
        self.root.mainloop()


# ════════════════════════════════════════════════════════════════════════════
# 工具函数
# ════════════════════════════════════════════════════════════════════════════


def _tier_emoji(name: str) -> str:
    """档名 → emoji 前缀。"""
    return {
        '普通档': '🟢',
        '中等档': '🟡',
        '高级档': '🟠',
    }.get(name, '⚪')


# ════════════════════════════════════════════════════════════════════════════
# 主入口（被 __main__.py 调用）
# ════════════════════════════════════════════════════════════════════════════


def main() -> int:
    """启动悬浮窗，返回退出码。"""
    w = TierWidget()
    w.mainloop()
    return 0


if __name__ == '__main__':
    sys.exit(main())
