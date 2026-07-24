# 安装与启动

## 环境要求

- Windows 10 或 Windows 11
- Python 3.11 或更新版本

安装 Python 时请勾选“加入环境变量”。可在 PowerShell 中确认版本：

```powershell
python --version
```

## 启动悬浮窗

进入项目目录后运行：

```powershell
cd D:\codering_widget
python scripts/launch_widget.py
```

无需安装额外依赖。启动后窗口显示在右下角；按住任意模型行拖动，按 Escape 关闭。

## 创建快捷启动文件

创建 `启动悬浮窗.bat`，写入：

```bat
@echo off
cd /d D:\codering_widget
python scripts\launch_widget.py
```

## 卸载

关闭悬浮窗后删除项目目录即可。若不再需要本地数据缓存，也可以删除：

```text
%USERPROFILE%\.codex_radar_cache.json
```

项目从不读取或改写 Codex 配置文件。
