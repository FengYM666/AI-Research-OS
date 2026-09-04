#!/usr/bin/env bash
# 一键安装本仓库推荐的第三方技能到 ~/.agents/skills/
# 用法（Git Bash / Linux / macOS）：bash install.sh
# Windows 用户请在 Git Bash 中运行（ZCode 用户自带）
set -e

SKILLS_DIR="$HOME/.agents/skills"
COMMANDS_DIR="$HOME/.agents/commands"
mkdir -p "$SKILLS_DIR" "$COMMANDS_DIR"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

echo "==> [1/4] superpowers 调试与验证两件套（obra/superpowers）"
git clone -q --depth 1 --filter=blob:none --sparse https://github.com/obra/superpowers "$TMP/superpowers"
(cd "$TMP/superpowers" && git sparse-checkout set skills/systematic-debugging skills/verification-before-completion)
cp -r "$TMP/superpowers/skills/systematic-debugging" "$TMP/superpowers/skills/verification-before-completion" "$SKILLS_DIR/"

echo "==> [2/4] phd-skills ML 实验纪律 12 件套 + 4 个斜杠命令（fcakyon/phd-skills）"
git clone -q --depth 1 https://github.com/fcakyon/phd-skills "$TMP/phd-skills"
cp -r "$TMP/phd-skills"/plugin/skills/* "$SKILLS_DIR/"
mkdir -p "$COMMANDS_DIR/phd-skills"
cp "$TMP/phd-skills"/plugin/commands/gaps.md "$TMP/phd-skills"/plugin/commands/xray.md \
   "$TMP/phd-skills"/plugin/commands/fortify.md "$TMP/phd-skills"/plugin/commands/factcheck.md \
   "$COMMANDS_DIR/phd-skills/"

echo "==> [3/4] 彭思达顶会写作方法论（Master-cai/Research-Paper-Writing-Skills）"
git clone -q --depth 1 --filter=blob:none --sparse https://github.com/Master-cai/Research-Paper-Writing-Skills "$TMP/rpw"
(cd "$TMP/rpw" && git sparse-checkout set research-paper-writing)
cp -r "$TMP/rpw/research-paper-writing" "$SKILLS_DIR/"

echo "==> [4/4] 出版级科研画图（K-Dense-AI/scientific-agent-skills）"
git clone -q --depth 1 --filter=blob:none --sparse https://github.com/K-Dense-AI/scientific-agent-skills "$TMP/kdense"
(cd "$TMP/kdense" && git sparse-checkout set skills/scientific-visualization)
cp -r "$TMP/kdense/skills/scientific-visualization" "$SKILLS_DIR/"

# 本仓库自研技能
echo "==> 安装本仓库自研的 paper-search 技能"
cp -r "$(dirname "$0")/../skills/paper-search" "$SKILLS_DIR/"

echo ""
echo "✅ 全部完成！重启你的 agent 客户端后生效。"
echo "📖 使用说明见 docs/技能操作指南.md"
