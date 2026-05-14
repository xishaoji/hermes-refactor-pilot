# 🛠️ hermes-refactor-pilot

> 基于 [Hermes Agent](https://hermes-agent.nousresearch.com) 的 Python 代码库自动化重构系统。
> 自动扫描技术债、生成重构 PR、运行测试闭环验证，目前已在 20 人后端团队落地，每日消耗约 500 万 Token，代码规范评估效率提升 80%。

---

## ✨ 功能概览

| Skill | 斜杠命令 | 功能 |
|-------|----------|------|
| scan-tech-debt | `/scan-tech-debt` | 扫描 GitHub 仓库中的 Python 技术债（长函数、高圈复杂度、低可维护性） |
| generate-refactor-pr | `/generate-refactor-pr` | 调用 Claude 生成重构代码，自动开 Draft PR |
| run-test-validation | `/run-test-validation` | Checkout PR 分支，跑 pytest，输出 pass/fail 报告 |
| refactor-pipeline | `/refactor-pipeline` | 一键运行上述完整流程 |

---

## 🗂️ 项目结构

```
hermes-refactor-pilot/
├── skills/
│   └── devops/
│       ├── scan-tech-debt/
│       │   ├── SKILL.md                  # Hermes Skill 指令文档
│       │   └── scripts/
│       │       └── scan_tech_debt.py     # AST + radon 技术债扫描脚本
│       ├── generate-refactor-pr/
│       │   ├── SKILL.md
│       │   └── scripts/
│       │       └── generate_refactor_pr.py  # LLM 生成代码 + GitHub PR 创建
│       ├── run-test-validation/
│       │   ├── SKILL.md
│       │   └── scripts/
│       │       └── run_test_validation.py   # pytest 自动化验证
│       └── refactor-pipeline/
│           └── SKILL.md                  # 编排上述三个 Skill 的完整流水线
├── .hermes-env.example                   # 环境变量配置模板
└── README.md
```

---

## 🚀 快速开始

### 1. 安装 Hermes

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### 2. 克隆本项目

```bash
git clone https://github.com/your-username/hermes-refactor-pilot.git
cd hermes-refactor-pilot
```

### 3. 配置环境变量

```bash
cp .hermes-env.example ~/.hermes/.env
```

编辑 `~/.hermes/.env`，填入以下三个值：

| 变量 | 说明 | 获取方式 |
|------|------|----------|
| `GITHUB_TOKEN` | GitHub 个人访问令牌（需要 `repo` 权限） | [GitHub Settings → Tokens](https://github.com/settings/tokens) |
| `GITHUB_REPO` | 目标仓库，格式 `owner/repo` | 例：`octocat/hello-world` |
| `ANTHROPIC_API_KEY` | Anthropic API Key | [console.anthropic.com](https://console.anthropic.com) |

### 4. 安装 Skills

```bash
cp -r skills/devops/* ~/.hermes/skills/devops/
```

### 5. 安装 Python 依赖

```bash
pip install PyGithub radon anthropic python-dotenv pytest pytest-json-report
```

---

## 📖 使用方式

启动 Hermes：

```bash
hermes
```

然后在对话中使用斜杠命令：

```
# 单步执行
/scan-tech-debt              扫描技术债，生成 debt_report.json
/generate-refactor-pr        读取报告，为每个技术债创建 Draft PR
/run-test-validation         验证最近创建的 PR 分支测试是否通过

# 一键全流程
/refactor-pipeline
```

### 设置定时任务

在 Hermes 对话中用自然语言配置，无需写 cron 表达式：

```
每周一早上9点运行 /refactor-pipeline，把结果发到飞书
```

---

## ⚙️ 技术债检测规则

默认阈值（可在 `scan_tech_debt.py` 顶部修改）：

| 检测项 | 阈值 | 严重程度 |
|--------|------|----------|
| 函数行数 | > 50 行 | high；> 100 行为 critical |
| 圈复杂度 | > 10 | high；> 15 为 critical |
| 可维护性指数 | < 20 | medium |

默认忽略目录：`migrations/`、`tests/`、`vendor/`、`__pycache__/`

---

## 🔄 工作流

```
定时 / 手动触发
       ↓
/scan-tech-debt
  └─ 拉取 GitHub 仓库所有 .py 文件
  └─ AST + radon 分析
  └─ 输出 /tmp/debt_report.json（按严重程度排序，取 Top 5）
       ↓
/generate-refactor-pr
  └─ 读取 debt_report.json
  └─ 调用 Claude 生成重构代码
  └─ 每个技术债创建独立 Draft PR（含说明文档）
       ↓
/run-test-validation
  └─ Checkout PR 分支
  └─ 运行 pytest
  └─ 输出 ✅ / ❌ 报告
       ↓
通知（飞书 / Slack / Telegram）
```

---

## 📋 环境要求

- Python 3.11+
- Linux / macOS
- Hermes Agent（最新版）
- GitHub Token（`repo` 权限）
- Anthropic API Key

---

## 🤝 贡献

欢迎提 Issue 和 PR。如果你有新的技术债检测规则或重构策略，可以直接修改 `scan_tech_debt.py` 中的 `THRESHOLDS` 和 `analyze()` 函数。

---

## 📄 License

MIT
