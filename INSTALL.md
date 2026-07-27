# 安装与启动

## 普通用户安装

只需要 Windows 10 或 Windows 11，不需要安装 Python：

1. 从 [Releases](https://github.com/lztpho/codex-tier-widget/releases/latest) 下载 `CodexTierWidget.exe`。
2. 将文件放到一个固定目录，例如 `%LOCALAPPDATA%\CodexTierWidget\`。
3. 双击 `CodexTierWidget.exe`。

首次运行会为当前 Windows 用户开启开机自启，不需要管理员权限。请先确定 EXE 的长期存放位置，再首次运行。

## 托盘与开机自启

- 按 `Escape` 隐藏悬浮窗，程序仍在后台运行。
- 右键托盘图标可以显示、隐藏、立即刷新或退出。
- 托盘菜单中的“开机自启”带勾时表示已开启；点击即可切换。
- EXE 被移动后，手动运行一次新位置的 EXE，会自动刷新自启路径。

## 从源码运行

开发者需要 Python 3.11 或更新版本：

```powershell
cd D:\codering_widget
python -m pip install -r requirements.txt
python scripts/launch_widget.py
```

构建单文件 EXE：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_windows_exe.ps1
```

输出文件位于 `dist\CodexTierWidget.exe`。

## 卸载

先在托盘菜单取消“开机自启”，再选择“退出程序”，最后删除 EXE。若不再需要本地数据缓存，也可以删除：

```text
%USERPROFILE%\.codex_radar_cache.json
```

项目从不读取或改写 Codex 配置文件。
