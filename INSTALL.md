# 安装指南 (Install Guide)

## 系统要求

- **操作系统**: Windows 10 / 11 (推荐); macOS / Linux 理论可用但未在 CI 验证
- **Python**: **3.11 或更新版本**（必须，依赖 `tomllib` 内置模块）

## 一、Windows 用户

### 1. 检查 Python 版本

打开 PowerShell 或 Git Bash：

```bash
python --version
```

期望输出：`Python 3.11.x` 或更高。

如果版本太旧或没装：

1. 访问 [python.org/downloads/](https://www.python.org/downloads/)
2. 下载 **Python 3.11+** 安装包
3. 运行安装包，**勾选 "Add Python to PATH"**（关键步骤！）
4. 重启 PowerShell 后重新检查版本

### 2. 获取项目代码

**方式 A：用 git（推荐）**

```bash
cd D:\
git clone https://github.com/<your-name>/codering_widget.git
cd codering_widget
```

**方式 B：直接下载 ZIP**

1. 打开 GitHub repo 页
2. 点 `Code` → `Download ZIP`
3. 解压到 `D:\codering_widget\`

### 3. 启动

方法一：直接启动

```bash
python src/codex_tier_widget/widget.py
```

方法二：作为 Python 模块启动（推荐，含 `__main__.py`）

```bash
python -m codex_tier_widget
```

> 注意：从 `src/` 父目录运行（即 `D:\codering_widget\`），而不是 `src/` 内

启动后桌面右下角立即出现 320×230 半透悬浮窗。

### 4. 桌面快捷方式（可选）

#### 4.1 双击启动的 .bat 文件

把以下内容保存到 `D:\codering_widget\启动 Codex 档位悬浮窗.bat`：

```bat
@echo off
cd /d "%~dp0"
python -m codex_tier_widget
pause
```

双击即可启动。

#### 4.2 生成 .lnk 快捷方式（带自定义图标）

在 PowerShell 中：

```powershell
$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut("$env:USERPROFILE\Desktop\Codex Tier Widget.lnk")
$lnk.TargetPath = "C:\Windows\py.exe"  # 或你的 python.exe 路径
$lnk.Arguments = "-m codex_tier_widget"
$lnk.WorkingDirectory = "D:\codering_widget"
$lnk.IconLocation = "shell32.dll,12"  # 系统图标
$lnk.Save()
```

（更详细的图标制作 / 自启脚本可放在 `scripts/` 下，欢迎贡献）

### 5. 开机自启（可选）

**方式 A：把上面的 .lnk 放到启动文件夹**

```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
```

**方式 B：用任务计划程序**

1. 打开「任务计划程序」(taskschd.msc)
2. 创建任务 → 触发器选「登录时」→ 操作选「启动程序」→ 程序 `python`，参数 `-m codex_tier_widget`，起始 `D:\codering_widget`

### 6. 升级

```bash
cd D:\codering_widget
git pull
```

如果改了 Python 接口，需要重装：

```bash
pip install -e .  # 可选，多数情况下不需要
```

## 二、macOS / Linux 用户

理论上能跑（tkinter + tomllib 都是跨平台），但以下功能未验证：

- 半透背景 alpha（macOS 上可能需要 `transparency=True`）
- always-on-top 在某些 GNOME / KDE 上行为可能不同

操作：

```bash
git clone https://github.com/<your-name>/codering_widget.git
cd codering_widget
python3.11 -m codex_tier_widget  # 用绝对路径的 Python 3.11
```

如果发现平台问题，欢迎开 Issue。

## 三、依赖说明

**0 外部 Python 依赖**！全部用标准库：

| 模块 | 用途 |
|---|---|
| `tkinter` | GUI |
| `urllib.request` | HTTP 拉取 codexradar 数据 |
| `tomllib` (Py 3.11+) | 读 `~/.codex/config.toml` |
| `pathlib` | 文件路径处理 |
| `json` / `re` / `time` / `sys` / `os` | 通用工具 |

所以不需要 `pip install` 任何东西。Windows 自带 Python 即可。

## 四、卸载

### 1. 关闭程序

任务栏 Codex 图标右键 → 退出。

### 2. 删除项目目录

```bash
rm -rf D:\codering_widget
```

### 3. 清理可选缓存

```bash
del %USERPROFILE%\.codex_radar_cache.json
del %USERPROFILE%\.codex_radar_widget.json
```

### 4. 如有 Codex 配置文件改动

工具只改 `~/.codex/config.toml` 的 `model` + `model_reasoning_effort` 两行，**不会删除其他配置**。如果要完全还原，手动编辑回原值即可。

## 五、故障排查（Trouble Shooting）

### 5.1 启动报 `ModuleNotFoundError: No module named 'tkinter'`

**Linux/Mac 上 tkinter 不在默认 Python**：需要装系统包：

```bash
# Debian / Ubuntu
sudo apt install python3.11-tk

# Fedora / RHEL
sudo dnf install python3.11-tkinter

# macOS (Homebrew Python)
brew install python-tk@3.11
```

**Windows**：重新装 Python，勾选「tcl/tk and IDLE」组件。

### 5.2 启动报 `AttributeError: module 'tomllib' not found`

Python 版本 < 3.11。装 3.11+。

工具会**自动 fallback 到正则匹配**模式下运行，但功能降级（详见 USAGE.md § "故障模式"）。

### 5.3 悬浮窗位置飘到屏幕外

启动时窗口定位用了 `winfo_screenwidth` 自动算右下角。某些多显示器 / 高 DPI 缩放下计算可能不准。

临时方案：编辑 `src/codex_tier_widget/config.py` 的 `WINDOW_*` 变量：

```python
WINDOW_WIDTH  = 320
WINDOW_HEIGHT = 230
# WINDOW_MARGIN = 24  ← 可以改成更小，让窗口靠右更近
```

### 5.4 "未检测到 Codex CLI 配置"

详见 [docs/FAQ.md](docs/FAQ.md)。

### 5.5 任何其他问题

去 GitHub Issues 搜一下 / 提一个新 issue，包含：

1. Windows 版本（如 Win 11 23H2）
2. Python 版本（`python --version`）
3. 完整报错（粘贴 log）
