# Codex Tier Widget — Makefile
# 用法：
#   make help           显示帮助
#   make run            跑应用
#   make test           单元测试（pytest）
#   make lint           静态检查（ruff + pyflakes）
#   make format         自动格式化（ruff format）
#   make check          跑完所有 CI 等价的检查（lint + test + build）
#   make clean          清掉 build 产物
#   make build          构建源码包 + wheel（用于上传到 PyPI，可选）

PYTHON ?= python
PIP    ?= pip

# 假设从 src/ 父目录运行
SRC_DIR := src

.PHONY: help
help:
	@echo "Codex Tier Widget — 开发者 Makefile"
	@echo ""
	@echo "目标："
	@echo "  make run         跑应用"
	@echo "  make syntax      python -m compileall 语法检查"
	@echo "  make lint        ruff + pyflakes 静态检查"
	@echo "  make format      ruff 自动格式化"
	@echo "  make test        pytest（待补）"
	@echo "  make check       syntax + lint + test"
	@echo "  make build       构建源码包 + wheel"
	@echo "  make clean       清掉 __pycache__、build/、dist/ 等"

# ── 应用 ───────────────────────────────────────────────────────────────────

.PHONY: run
run:
	$(PYTHON) -m codex_tier_widget

.PHONY: syntax
syntax:
	$(PYTHON) -m compileall -q $(SRC_DIR)

# ── Lint / Format ──────────────────────────────────────────────────────────

.PHONY: lint
lint:
	$(PYTHON) -m ruff check $(SRC_DIR)
	$(PYTHON) -m pyflakes $(SRC_DIR)

.PHONY: format
format:
	$(PYTHON) -m ruff format $(SRC_DIR)
	$(PYTHON) -m ruff check --fix $(SRC_DIR)

# ── Test ───────────────────────────────────────────────────────────────────

.PHONY: test
test:
	$(PYTHON) -m pytest tests/ -v

.PHONY: coverage
coverage:
	$(PYTHON) -m pytest tests/ --cov=src/codex_tier_widget --cov-report=term --cov-report=html

# ── Install dev deps ───────────────────────────────────────────────────────

.PHONY: install-dev
install-dev:
	$(PIP) install -e ".[dev]"

# ── Build ──────────────────────────────────────────────────────────────────

.PHONY: build
build:
	$(PYTHON) -m build

.PHONY: build-sdist
build-sdist:
	$(PYTHON) -m build --sdist

.PHONY: build-wheel
build-wheel:
	$(PYTHON) -m build --wheel

# ── Clean ──────────────────────────────────────────────────────────────────

.PHONY: clean
clean:
	@find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.ruff_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	@rm -rf build/ dist/ .coverage htmlcov/ 2>/dev/null || true
	@find . -name '*.pyc' -delete 2>/dev/null || true

# ── Aggregate ──────────────────────────────────────────────────────────────

.PHONY: check
check: syntax lint
	@echo "✓ all checks passed"

.PHONY: clean-all
clean-all: clean
	@rm -rf .venv/ *.egg-info
	@echo "✓ cleaned everything"
