---
name: 🐛 Bug Report
about: 工具出问题？告诉我现象、复现步骤、版本
title: '[BUG] '
labels: bug
assignees: ''
---

## 现象 (Symptom)

悬浮窗出现什么问题？比如：

- 启动报 `...` 错误
- 按按钮无反应
- 第 4 档不显示 / 显示错误
- 颜色一直灰色 / 一直红的
- 窗口位置飘到屏幕外

## 复现步骤 (Steps to Reproduce)

1. 启动 `python -m codex_tier_widget`
2. ...
3. 看到什么 / 期望看到什么

## 环境 (Environment)

```yaml
OS:           Windows 11 23H2   (or "macOS 14.5")
Python:       3.11.9            (output of `python --version`)
Codex 客户端: CLI / VSCode / Desktop App / Web (circle)
Codex model:  gpt-5-codex       (output of `grep ^model ~/.codex/config.toml`)
```

## 期望 (Expected)

应该看到什么？

## 实测 (Actual)

实际看到什么？

## 错误输出 (Error Output)

粘贴完整报错（如果启动就崩了）：

```
Traceback (most recent call last):
  ...
  AttributeError: ...
```

## 截图 (Screenshots)

如果窗口显示有问题，截图比文字描述清楚。

## 其他信息 (Additional Context)

你做了什么尝试？比如：

- 重启过 widget
- 删了缓存
- 重新装了 Python

## 隐私检查 (Privacy Check)

- [ ] 我已检查上面的报错 / 路径 **不包含** API key / token / 个人信息
- [ ] 我没粘贴我自己项目的代码内容

> 工具**不会**发送你的代码到任何地方，只拉 `codexradar.com/data/intelligence-efficiency.json`。
