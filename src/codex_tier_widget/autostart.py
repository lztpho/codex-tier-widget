"""Windows 当前用户开机自启管理。"""

from __future__ import annotations

import base64
import os
import subprocess
import sys
from pathlib import Path

SETTINGS_KEY = r'Software\CodexTierWidget'
CONFIGURED_VALUE = 'AutoStartConfigured'
SHORTCUT_NAME = 'CodexTierWidget.lnk'
LEGACY_RUN_KEY = r'Software\Microsoft\Windows\CurrentVersion\Run'
LEGACY_RUN_VALUE = 'CodexTierWidget'


class AutoStartManager:
    """通过当前用户“启动”文件夹管理开机自启。"""

    def __init__(self) -> None:
        self.last_error: OSError | None = None

    @property
    def supported(self) -> bool:
        """仅 Windows 支持快捷方式自启。"""
        return sys.platform == 'win32'

    @property
    def shortcut_path(self) -> Path:
        """返回当前用户启动文件夹中的快捷方式路径。"""
        appdata = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
        return (
            appdata
            / 'Microsoft'
            / 'Windows'
            / 'Start Menu'
            / 'Programs'
            / 'Startup'
            / SHORTCUT_NAME
        )

    @property
    def command(self) -> str:
        """返回快捷方式最终执行的完整命令。"""
        target, arguments, _working_directory = self._launch_parts()
        return subprocess.list2cmdline([target, *arguments])

    def initialize_default_enabled(self) -> bool:
        """首次运行默认启用；以后尊重用户在托盘中的选择。"""
        if not self.supported:
            return False
        self._remove_legacy_run_value()
        if not self._is_configured():
            return self.set_enabled(True)
        if self.is_enabled():
            return self.set_enabled(True)
        return True

    def is_enabled(self) -> bool:
        """读取当前自启状态。"""
        return self.supported and self.shortcut_path.is_file()

    def toggle(self) -> bool | None:
        """切换自启并返回新状态；失败返回 None。"""
        enabled = not self.is_enabled()
        return enabled if self.set_enabled(enabled) else None

    def set_enabled(self, enabled: bool) -> bool:
        """创建或删除当前用户启动文件夹中的快捷方式。"""
        if not self.supported:
            return False

        self.last_error = None
        try:
            if enabled:
                self._create_shortcut()
            else:
                self.shortcut_path.unlink(missing_ok=True)
            self._mark_configured()
            self._remove_legacy_run_value()
            return True
        except (OSError, subprocess.SubprocessError) as exc:
            self.last_error = OSError(str(exc))
            return False

    def _launch_parts(self) -> tuple[str, list[str], str]:
        if getattr(sys, 'frozen', False):
            executable = Path(sys.executable)
            return str(executable), [], str(executable.parent)

        python = Path(sys.executable)
        pythonw = python.with_name('pythonw.exe')
        executable = pythonw if pythonw.exists() else python
        project_root = Path(__file__).resolve().parents[2]
        launcher = project_root / 'scripts' / 'launch_widget.py'
        if launcher.exists():
            return str(executable), [str(launcher)], str(project_root)
        return str(executable), ['-m', 'codex_tier_widget'], str(Path.cwd())

    def _create_shortcut(self) -> None:
        target, arguments, working_directory = self._launch_parts()
        shortcut = self.shortcut_path
        shortcut.parent.mkdir(parents=True, exist_ok=True)

        script = '\n'.join(
            (
                '$Shell = New-Object -ComObject WScript.Shell',
                f"$Shortcut = $Shell.CreateShortcut('{self._ps_quote(str(shortcut))}')",
                f"$Shortcut.TargetPath = '{self._ps_quote(target)}'",
                f"$Shortcut.Arguments = '{self._ps_quote(subprocess.list2cmdline(arguments))}'",
                f"$Shortcut.WorkingDirectory = '{self._ps_quote(working_directory)}'",
                "$Shortcut.Description = 'Codex Tier Widget'",
                '$Shortcut.Save()',
            )
        )
        encoded = base64.b64encode(script.encode('utf-16le')).decode('ascii')
        completed = subprocess.run(
            [
                'powershell.exe',
                '-NoProfile',
                '-NonInteractive',
                '-EncodedCommand',
                encoded,
            ],
            check=False,
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
            timeout=15,
        )
        if completed.returncode != 0 or not shortcut.is_file():
            detail = completed.stderr.decode(errors='replace').strip()
            raise OSError(detail or '无法创建开机自启快捷方式')

    def _is_configured(self) -> bool:
        import winreg

        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                SETTINGS_KEY,
                0,
                winreg.KEY_QUERY_VALUE,
            ) as key:
                value, _value_type = winreg.QueryValueEx(key, CONFIGURED_VALUE)
                return bool(value)
        except FileNotFoundError:
            return False
        except OSError as exc:
            self.last_error = exc
            return False

    def _mark_configured(self) -> None:
        import winreg

        with winreg.CreateKeyEx(
            winreg.HKEY_CURRENT_USER,
            SETTINGS_KEY,
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            winreg.SetValueEx(key, CONFIGURED_VALUE, 0, winreg.REG_DWORD, 1)

    def _remove_legacy_run_value(self) -> None:
        import winreg

        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                LEGACY_RUN_KEY,
                0,
                winreg.KEY_SET_VALUE,
            ) as key:
                winreg.DeleteValue(key, LEGACY_RUN_VALUE)
        except FileNotFoundError:
            self.last_error = None
        except OSError as exc:
            self.last_error = exc

    @staticmethod
    def _ps_quote(value: str) -> str:
        return value.replace("'", "''")
