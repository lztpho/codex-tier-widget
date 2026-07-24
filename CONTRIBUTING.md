# 贡献指南 (Contributing)

欢迎 PR / Issue！本项目目标是「轻量、便携、跨机部署」，请保持代码风格一致。

## 一、开发环境

```bash
# 1. Fork + clone
git clone https://github.com/<your-name>/codering_widget.git
cd codering_widget

# 2. 不需要虚拟环境或 pip install（0 依赖）
#    但推荐用 venv 把开发依赖独立开
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS / Linux

# 3. 安装开发依赖（可选，只为跑 lint / test）
pip install -e ".[dev]"

# 4. 跑起来
python -m codex_tier_widget
```

## 二、项目结构

```
codering_widget/
├── src/
│   └── codex_tier_widget/      ← 主代码（可 pip 安装）
│       ├── __init__.py
│       ├── __main__.py         ← python -m entry
│       ├── widget.py           ← tkinter UI 主循环
│       ├── data.py             ← 拉 codexradar 数据
│       ├── codex_config.py     ← 读/写 ~/.codex/config.toml
│       ├── color.py            ← 性价比 → 颜色
│       └── config.py           ← 静态配置（TIERS / 颜色阈值 / URL）
├── docs/                       ← 详细文档
│   ├── ARCHITECTURE.md
│   └── FAQ.md
├── tools/                      ← 开发者脚本
├── scripts/                    ← 用户级脚本（启动 / 卸载）
├── assets/                     ← 图标 / 截图
├── .github/                    ← Issue 模板 + CI
│   ├── ISSUE_TEMPLATE/
│   └── workflows/
├── tests/                      ← (尚未建立，欢迎 PR)
├── pyproject.toml              ← 现代项目元数据
├── requirements.txt            ← 0 依赖
├── Makefile                    ← make run / make test / make lint
├── README.md / README.en.md
├── INSTALL.md
├── USAGE.md
├── CHANGELOG.md
├── CONTRIBUTING.md             ← 你正在读的
├── LICENSE                     ← MIT
└── .gitignore
```

## 三、代码风格

### 3.1 Python

- **PEP 8** 风格，line length **100**
- **中文 docstring**，类型注解（`from __future__ import annotations`）
- 模块顶部用三引号中文 docstring 简述用途
- 函数 docstring：单行 `"""一句话。"""`，多行用 `"""\n 长描述。\nArgs:\n    xxx: 描述。\n"""`

### 3.2 Import 顺序

```python
from __future__ import annotations

# 标准库
import json
import re
from pathlib import Path

# 第三方（暂无）

# 本项目
from . import config
```

### 3.3 注释

```python
# 单行短注释
x = compute()  # 行内说明

# 多行注释（解释一段逻辑）
# 第一段说明
# 第二段说明
```

注释用中文，标点英文半角。

### 3.4 命名

- 函数 / 变量：`snake_case`
- 类：`PascalCase`
- 常量：`UPPER_SNAKE_CASE`
- 私有：下划线前缀 `_helper()`

## 四、提交规范

### 4.1 Commit message

用 **Conventional Commits** 风格（参考：[conventionalcommits.org](https://www.conventionalcommits.org/)）：

```
feat: 添加自定义档下拉菜单
fix: 修正 mtime 轮询在网络盘上的延迟
docs: 更新 README 的部署说明
refactor: 把 widget.py 拆成 widget.py + tier_row.py
test: 添加 color.py 的单元测试
chore: 升级 pyproject.toml 到 setuptools>=68
```

### 4.2 分支策略

- `main` 主分支，保持可发布状态
- `feature/<name>` 开发新功能
- `fix/<issue-number>` 修 bug
- `docs/<name>` 仅文档

### 4.3 PR checklist

- [ ] 我跑了 `python -m compileall src/` 没有语法错误
- [ ] 我跑了核心场景（启动 → 按按钮 → 看到悬浮窗）的端到端测试
- [ ] 我更新了相关文档（README/USAGE/docs）
- [ ] 我没引入新的外部依赖（仍是 0 依赖）

## 五、添加新功能 → 提案

如果你要加的不是 trivial 的功能，建议先开 Issue 讨论，避免做出来跟项目目标冲突：

- ✅ 接受：纯 Python / 纯标准库 / 不破坏 0 依赖 / 不增加显著包大小
- ✅ 接受：跨平台修复（macOS/Linux 兼容性）
- ⚠️ 需要讨论：是否引入 `pystray`（系统托盘）？`Pillow`（图标）？
- ❌ 拒绝：纯 GUI 重写（PySide6 / PyQt）—— 用户明确要求 0 依赖部署
- ❌ 拒绝：打包成 .exe——避免供应链膨胀

## 六、测试

目前没有自动化测试套件，欢迎贡献：

```bash
# 临时验证：手动跑 syntax check
python -m compileall src/

# 临时验证：手动跑核心功能
python -m codex_tier_widget  # 看到 UI 起来
```

未来预期：

- `tests/test_color.py` - 单元测试染色的边界条件
- `tests/test_codex_config.py` - mock 文件系统测试读写
- `tests/test_data.py` - mock urllib 测试拉数 + fallback 缓存

## 七、CI

PR 提交后会自动跑 `.github/workflows/syntax-check.yml`：

- Python 3.11+ 编译检查（`python -m compileall`）
- import smoke test
- 拼写检查

## 八、行为准则

我们承诺：参与本项目的一切互动都要专业、包容、互相尊重。详见 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)（如有）。

## 九、报告安全问题

**不要**在公开 Issue 里报告安全问题。请发邮件给 maintainer（查看 GitHub repo 的 OWNERS 文件）。

## 十、License 同意

提交 PR 即同意你的贡献按本项目的 MIT License 发布。
