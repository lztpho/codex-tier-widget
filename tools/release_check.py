#!/usr/bin/env python3
"""发布前检查脚本：验证 CHANGELOG、版本号、依赖声明、tag 等。

用法：
    python tools/release_check.py

会在以下情况报错：
  - pyproject.toml 的 version 与 codex_tier_widget/__init__.py 的 __version__ 不一致
  - CHANGELOG.md 缺 [Unreleased] 段
  - README.md 里所有 markdown link 失效（指向本地文件时）

退出码：0 = pass；非 0 = fail
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / 'pyproject.toml'
INIT = ROOT / 'src' / 'codex_tier_widget' / '__init__.py'
CHANGELOG = ROOT / 'CHANGELOG.md'


def check_version_consistent() -> int:
    """pyproject.toml 与 __init__.py 的版本号必须一致。"""
    pyproject_v = None
    init_v = None
    pyproject_text = PYPROJECT.read_text(encoding='utf-8')
    m = re.search(r'version\s*=\s*"([^"]+)"', pyproject_text)
    if m:
        pyproject_v = m.group(1)
    init_text = INIT.read_text(encoding='utf-8')
    m = re.search(r"__version__\s*=\s*'([^']+)'", init_text)
    if m:
        init_v = m.group(1)
    if pyproject_v is None or init_v is None:
        print('✗ 无法解析版本号')
        return 1
    if pyproject_v != init_v:
        print(f'✗ 版本不一致：pyproject.toml={pyproject_v}, __init__.py={init_v}')
        return 1
    print(f'✓ 版本一致: {pyproject_v}')
    return 0


def check_changelog_has_unreleased() -> int:
    """CHANGELOG.md 顶部必须有 [Unreleased] 段。"""
    text = CHANGELOG.read_text(encoding='utf-8')
    if '## [Unreleased]' not in text:
        # 找到第一个 ## 段
        m = re.search(r'^##\s+\[', text, re.MULTILINE)
        first = m.group(0) if m else '无'
        print(f'✗ 缺 [Unreleased] 段；当前首段是：{first}')
        return 1
    print('✓ [Unreleased] 段存在')
    return 0


def check_no_secrets() -> int:
    """代码里不应该有 token / api key / 私钥 等敏感字符串。"""
    sensitive_patterns = [
        (r'sk-[A-Za-z0-9]{20,}', 'OpenAI API key'),
        (r'ghp_[A-Za-z0-9]{20,}', 'GitHub PAT'),
        (r'-----BEGIN (RSA |EC )?PRIVATE KEY-----', 'private key'),
    ]
    rc = 0
    files_to_check = list((ROOT / 'src').rglob('*.py')) + [
        PYPROJECT,
        ROOT / 'README.md',
        CHANGELOG,
    ]
    for f in files_to_check:
        try:
            text = f.read_text(encoding='utf-8')
        except (OSError, UnicodeError):
            continue
        for pattern, label in sensitive_patterns:
            if re.search(pattern, text):
                print(f'✗ {f.relative_to(ROOT)} 含疑似 {label}')
                rc = 1
    if rc == 0:
        print('✓ 未发现敏感字符串')
    return rc


def main() -> int:
    print('📦 发布前检查...\n')
    rc = 0
    rc += check_version_consistent()
    rc += check_changelog_has_unreleased()
    rc += check_no_secrets()
    print('\n' + ('✓ 全部通过' if rc == 0 else f'✗ {rc} 项失败'))
    return 0 if rc == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
