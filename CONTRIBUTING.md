# 贡献指南

欢迎提交问题、建议和改进。请保持项目的核心边界：紧凑三行展示、轻量运行依赖、不读取或控制 Codex。

## 本地开发

```powershell
git clone https://github.com/lztpho/codex-tier-widget.git
cd codex-tier-widget
python -m pip install -r requirements.txt
python scripts/launch_widget.py
```

开发校验：

```powershell
python tools/dev_check.py all
python tools/release_check.py
powershell -ExecutionPolicy Bypass -File scripts/build_windows_exe.ps1
```

## 项目结构

```text
src/codex_tier_widget/
├── widget.py       界面、拖动、刷新、排序与生命周期
├── tray.py         系统托盘图标和退出菜单
├── autostart.py    Windows 当前用户开机自启
├── data.py         公开数据和本机缓存
├── color.py        性价比计算与显示格式
├── config.py       档位、IQ 门槛、数据和界面配置
├── __init__.py     包元数据
└── __main__.py     模块启动入口
scripts/
├── launch_widget.py       本地源码启动脚本
└── build_windows_exe.ps1  Windows EXE 构建脚本
tools/
├── dev_check.py      开发检查
└── release_check.py  发布前检查
```

## 代码约定

- Python 3.11+；运行时使用 `pystray` 和 `Pillow` 提供系统托盘图标。
- 使用类型注解与中文文档字符串。
- 新功能不得引入 Codex 配置读写、模型切换或进程控制。
- 修改排序、数据解析或窗口尺寸后，应补充对应的运行验证。

## 提交信息

使用简短、明确的 Conventional Commits 格式：

```text
feat: 增加 IQ 门槛排序
fix: 修正窗口拖动偏移
docs: 重写开源文档
refactor: 精简公开数据解析
```

提交前确认开发检查通过，并在变更影响用户行为时更新 `CHANGELOG.md`。
