"""codex_tier_widget.codex_config — 读写 ~/.codex/config.toml + mtime 监测。

Codex CLI 的档位在 `~/.codex/config.toml` 里通过两行配置控制：

    model = "gpt-5-codex"
    model_reasoning_effort = "high"

切档位 = 改这两行（其他字段保留）。运行中修改需要重启 Codex CLI 才生效
（这是 OpenAI Codex 自身的设计，本工具无法绕过）。

本模块提供：
  - CodexConfig.exists()   探测文件存在
  - CodexConfig.mtime()    当前 mtime，用于变化探测
  - CodexConfig.read()     读 model + model_reasoning_effort → dict
  - CodexConfig.write()    原子写两行，保留其他字段
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# tomllib 在 Python 3.11+ 才内置；3.10 及以下用正则 fallback
_tomllib: object | None = None
if sys.version_info >= (3, 11):
    try:
        import tomllib as _tomllib  # type: ignore[assignment]
    except ImportError:
        _tomllib = None


def _config_path() -> Path:
    """返回 Codex 配置文件路径（推迟到第一次调用时求值）。"""
    from . import config
    return config.codex_config_path()


class CodexConfig:
    """Codex 配置文件读写器。

    单线程使用。UI 主循环里调用 mtime() / read() / write()。

    Attributes:
        path:       配置文件路径（绝对）
        last_mtime: 上一次观察到的 mtime，用于 detect change
    """

    def __init__(self, path: Path | None = None) -> None:
        """Args:
            path: 自定义路径；None 时走 config.codex_config_path()
        """
        self.path: Path = path or _config_path()
        self.last_mtime: float = 0.0

    # ── 探测 ────────────────────────────────────────────────────────────

    def exists(self) -> bool:
        """配置文件是否存在。"""
        try:
            return self.path.exists()
        except OSError:
            return False

    def mtime(self) -> float:
        """当前 mtime，文件不存在则返回 0。"""
        if not self.exists():
            return 0.0
        try:
            return self.path.stat().st_mtime
        except OSError:
            return 0.0

    def changed(self) -> bool:
        """检测文件是否变了（比上次 mtime 更新）。读一次会更新 last_mtime。"""
        cur = self.mtime()
        if cur != self.last_mtime:
            self.last_mtime = cur
            return True
        return False

    # ── 读 ──────────────────────────────────────────────────────────────

    def read(self) -> dict | None:
        """读取 model + model_reasoning_effort。

        Returns:
            {'model': str, 'effort': str | None}，任何字段缺失该值为 None
            失败（文件不存在 / 权限 / 解析错）返回 None
        """
        if not self.exists():
            return None
        try:
            text = self.path.read_text(encoding='utf-8')
        except OSError:
            return None

        # 优先 tomllib
        if _tomllib is not None:
            try:
                d = _tomllib.loads(text)  # type: ignore[attr-defined]
                return {
                    'model':  d.get('model'),
                    'effort': d.get('model_reasoning_effort'),
                }
            except _tomllib.TOMLDecodeError:  # type: ignore[attr-defined]
                pass
            except Exception:
                pass

        # fallback：正则匹配
        return self._read_regex(text)

    @staticmethod
    def _read_regex(text: str) -> dict | None:
        """正则兜底（兼容 Python < 3.11 + 手写 TOML）。"""
        m_model = re.search(r'^\s*model\s*=\s*[\'"]([^\'"]+)[\'"]', text, re.M)
        if not m_model:
            return None
        m_eff = re.search(
            r'^\s*model_reasoning_effort\s*=\s*[\'"]([^\'"]+)[\'"]',
            text, re.M,
        )
        return {
            'model':  m_model.group(1),
            'effort': m_eff.group(1) if m_eff else None,
        }

    # ── 写 ──────────────────────────────────────────────────────────────

    def write(self, model: str, effort: str) -> bool:
        """原子写：替换或追加 model + model_reasoning_effort 两行，保留其他字段。

        Args:
            model:   OpenAI 模型 ID，如 'gpt-5-codex'
            effort:  推理强度，如 'xhigh' / 'medium' / 'high'

        Returns:
            True 成功，False 失败（文件不存在 / 权限 / 写错）
        """
        if not self.exists():
            return False

        try:
            text = self.path.read_text(encoding='utf-8')
        except OSError:
            return False

        # 替换或追加 model
        if re.search(r'^\s*model\s*=', text, re.M):
            text = re.sub(
                r'^(\s*)model\s*=.*$',
                rf'\1model = "{model}"',
                text, count=1, flags=re.M,
            )
        else:
            if not text.endswith('\n'):
                text += '\n'
            text += f'model = "{model}"\n'

        # 替换或追加 model_reasoning_effort
        if re.search(r'^\s*model_reasoning_effort\s*=', text, re.M):
            text = re.sub(
                r'^(\s*)model_reasoning_effort\s*=.*$',
                rf'\1model_reasoning_effort = "{effort}"',
                text, count=1, flags=re.M,
            )
        else:
            if not text.endswith('\n'):
                text += '\n'
            text += f'model_reasoning_effort = "{effort}"\n'

        # 原子写：先写 .tmp，再 os.replace（POSIX atomic，Windows 自 Vista 起 atomic）
        tmp = self.path.with_suffix(self.path.suffix + '.tmp')
        try:
            tmp.write_text(text, encoding='utf-8')
            os.replace(tmp, self.path)
            return True
        except OSError:
            return False
        finally:
            # 清理残留 tmp
            if tmp.exists():
                try:
                    tmp.unlink()
                except OSError:
                    pass
