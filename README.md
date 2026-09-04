# zcode-research-setup

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)]()
[![Client](https://img.shields.io/badge/client-ZCode%20%7C%20Claude%20Code-green)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)]()

> 把 AI 编程助手调教成靠谱的**学术科研搭子**：不编论文、不乱改代码、查文献走权威源、写论文懂顶会套路。
>
> 一套开箱即用的 Agent 配置方案：行为纪律 + 技能组合 + MCP 服务器 + 网络自动化，覆盖"定方向 → 查文献 → 复现实验 → 画图 → 写论文 → 投稿防守"全链条。

[English README](README_EN.md) · [使用指南](docs/技能操作指南.md) · [技能清单](skills/README.md)

---

## ✨ 为什么值得用

| 痛点 | 本方案 |
|------|--------|
| 😤 AI 编造假论文引用 | 论文检索五要素核实制：标题/作者/年份/会议/链接必须来自同一条真实记录，查不到就明说 |
| 😤 AI 说"修好了"其实没修 | `verification-before-completion`：拿不出运行证据不许说完成 |
| 😤 出 bug 越改越乱 | `systematic-debugging`：先复现→挖根因→再修→验证，四步流程 |
| 😤 训练跑 50 小时发现配置错了 | `launch` 起飞前检查单 + `compare` 同 epoch 对齐对比 |
| 😤 投稿被审稿人秒杀 | `reviewer-defense` 预判审稿问题 + `/phd-skills:factcheck` 逐条查假引用 |
| 😤 开关代理后终端就断网 | `proxy-auto-detect.sh`：自动感应系统代理开关，终端永远在线 |

## 🔬 科研工作流全景

```mermaid
graph LR
    A["定方向<br>/phd-skills:gaps"] --> B["查文献<br>paper-search MCP"]
    B --> C["复现<br>reproduce"]
    C --> D["跑实验<br>launch / compare / debug"]
    D --> E["画图<br>scientific-visualization"]
    E --> F["写论文<br>research-paper-writing"]
    F --> G["投稿防守<br>fortify / factcheck"]
```

## 🚀 快速开始

```bash
# 1. 克隆本仓库
git clone https://github.com/FengYM666/zcode-research-setup.git
cd zcode-research-setup

# 2. 一键安装全部推荐技能（Git Bash / Linux / macOS）
bash scripts/install.sh

# 3. 按需复制配置（详见下方"包含什么"）
# 4. 重启你的 agent 客户端，开聊！
```

试试这句：*"帮我找近三年 3D Gaussian Splatting 压缩方向的顶会论文，要有代码的"*

## 📦 包含什么

| 路径 | 说明 |
|------|------|
| `AGENTS.md` | **行为纪律**：执行前确认、计划拷问、改完代码强制验证（放用户目录全局生效） |
| `skills/` | 自研 `paper-search` 技能 + 精选第三方技能清单（附一键安装脚本） |
| `scripts/proxy-auto-detect.sh` | 终端代理自动感应（每次开 shell 读系统代理状态，开关梯子都不掉线） |
| `scripts/notify.ps1` | 任务完成/出错的声音提醒 hook（Windows） |
| `config/config.example.json` | MCP 服务器配置样例（paper-search + Context7），已脱敏 |
| `docs/技能操作指南.md` | 新手友好的中文使用手册：每个环节"你就这么说" |

## 🧠 设计哲学

1. **流程 > 知识**：只装教 agent "怎么干活"的技能；知识类技能模型本来就会，装了是噪音
2. **证据 > 声称**：任何"完成/修好/发表"的声称必须附可验证的证据
3. **少即是多**：46 个精选技能 > 163 个全家桶，上下文越干净 agent 越聪明
4. **机制 > 自觉**：能写成 hook/脚本的规则，不靠模型自觉

## ❓ 常见问题

**Q: 技能太多会不会互相冲突？**
A: 不会。每个技能只在匹配场景触发，且我们刻意去掉了重叠的知识类技能。

**Q: 中国大陆网络能用吗？**
A: 原生适配。`proxy-auto-detect.sh` 自动感应梯子开关；谷歌学术检索自动走代理；jsdelivr 镜像作为免代理备胎。

**Q: 支持哪些客户端？**
A: 开发于 ZCode，技能遵循开放 [Agent Skills](https://agentskills.io) 标准，Claude Code / Cursor / Codex 等均可用。

## 🙏 致谢

本方案站在这些优秀开源项目的肩膀上：[obra/superpowers](https://github.com/obra/superpowers) · [fcakyon/phd-skills](https://github.com/fcakyon/phd-skills) · [Master-cai/Research-Paper-Writing-Skills](https://github.com/Master-cai/Research-Paper-Writing-Skills)（致谢[彭思达](https://github.com/pengsida)老师）· [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) · [openags/paper-search-mcp](https://github.com/openags/paper-search-mcp) · [anthropics/skills](https://github.com/anthropics/skills)

---

如果这套方案帮到了你，欢迎点个 ⭐ Star 支持一下！
