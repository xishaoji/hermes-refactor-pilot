#!/usr/bin/env bash
# hermes-refactor-pilot 安装脚本
# 用法: bash install.sh

set -e

HERMES_DIR="$HOME/.hermes"
ENV_FILE="$HERMES_DIR/.env"
SKILLS_SRC="$(cd "$(dirname "$0")/skills/devops" && pwd)"
SKILLS_DST="$HERMES_DIR/skills/devops"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  hermes-refactor-pilot 安装程序"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── 1. 检查 Hermes 是否已安装 ────────────────────────────────
if ! command -v hermes &>/dev/null; then
  echo "❌ 未检测到 hermes 命令，请先安装 Hermes："
  echo "   curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash"
  exit 1
fi
echo "✅ Hermes 已安装：$(hermes --version 2>/dev/null || echo '版本未知')"

# # ── 2. 安装 Python 依赖 ─────────────────────────────────────
# echo ""
# echo "📦 安装 Python 依赖（PyGithub radon python-dotenv pytest pytest-json-report）..."
# pip install --quiet PyGithub radon python-dotenv pytest pytest-json-report
# echo "✅ 依赖安装完成"

# ── 3. 安装 Skills ──────────────────────────────────────────
echo ""
echo "🔧 安装 Skills 到 $SKILLS_DST ..."
mkdir -p "$SKILLS_DST"
cp -r "$SKILLS_SRC"/. "$SKILLS_DST/"
echo "✅ Skills 安装完成："
find "$SKILLS_DST" -name "SKILL.md" | sed "s|$HOME|~|g" | sort | sed 's/^/   /'

# ── 4. 安全合并环境变量（不覆盖已有 .env）──────────────────
echo ""
echo "⚙️  配置环境变量 ..."
mkdir -p "$HERMES_DIR"
touch "$ENV_FILE"

added=0
skipped=0

while IFS= read -r line; do
  # 跳过注释行和空行
  [[ "$line" =~ ^#.*$ || -z "${line// }" ]] && continue

  key="${line%%=*}"

  if grep -q "^${key}=" "$ENV_FILE" 2>/dev/null; then
    echo "   ⏭️  跳过 $key（已存在，保留原值）"
    ((skipped++)) || true
  else
    echo "$line" >> "$ENV_FILE"
    echo "   ✅ 已添加 $key"
    ((added++)) || true
  fi
done < "$(dirname "$0")/.hermes-env.example"

echo ""
if [ "$added" -gt 0 ]; then
  echo "⚠️  新增了 $added 个变量，请编辑 ~/.hermes/.env 填入真实值："
  grep -E "^(GITHUB_TOKEN|GITHUB_REPO)=" "$ENV_FILE" | sed 's/^/   /'
else
  echo "✅ 所有变量已存在，.env 未改动"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  安装完成！启动 Hermes 后可使用："
echo "    /scan-tech-debt       扫描技术债"
echo "    /generate-refactor-pr 生成重构 PR"
echo "    /run-test-validation  验证测试"
echo "    /refactor-pipeline    一键全流程"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
