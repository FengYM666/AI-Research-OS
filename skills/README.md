# 技能清单（Skills Manifest）

本仓库的核心理念：**技能宁缺毋滥**。只装"流程类"技能（教 agent 怎么干活），不装"知识类"技能（agent 本来就会的东西，装了只会稀释触发准确率、白占上下文）。

## 一键安装

```bash
bash scripts/install.sh
```

## 学术研究链（核心）

| 技能 | 来源 | 干什么 |
|------|------|--------|
| `paper-search` | ⭐ 本仓库自研 | 论文检索规范：只用权威源、五要素核实、禁止编造 |
| `reproduce` / `debug` / `launch` / `compare` | [fcakyon/phd-skills](https://github.com/fcakyon/phd-skills) | 论文复现、实验报错诊断、长训练起飞检查、同 epoch 实验对比 |
| `experiment-design` / `literature-research` / `dataset-curation` | 同上 | 消融设计、文献调研、数据集偏差分析 |
| `paper-writing` / `paper-verification` / `reviewer-defense` / `research-publishing` / `latex-setup` | 同上 | 论文写作一致性、数字对代码审计、预判审稿人、开源发布、LaTeX 环境 |
| `research-paper-writing` | [Master-cai/Research-Paper-Writing-Skills](https://github.com/Master-cai/Research-Paper-Writing-Skills)（彭思达方法论） | 顶会各章节写作（Abstract/Intro/Method/Experiments） |
| `scientific-visualization` | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | 出版级图表，带数据诚信护栏 |

**斜杠命令**（安装脚本会一并装到 `~/.agents/commands/phd-skills/`）：
`/phd-skills:gaps`（找研究空白）· `/phd-skills:xray`（论文对代码审计）· `/phd-skills:fortify`（选最强消融）· `/phd-skills:factcheck`（查假引用）

## 工程质量

| 技能 | 来源 | 干什么 |
|------|------|--------|
| `systematic-debugging` | [obra/superpowers](https://github.com/obra/superpowers) | 四阶段根因调试：复现→定位→修复→验证 |
| `verification-before-completion` | 同上 | 拿不出运行证据不许说"完成" |

## 配套 MCP 服务器

| 服务器 | 配置 | 用途 |
|--------|------|------|
| [paper-search-mcp](https://github.com/openags/paper-search-mcp) | `config/config.example.json` | 20 个学术源检索/下载/读全文 |
| [Context7](https://context7.com) | 同上（免费免 key） | 查库的最新官方文档，治 API 幻觉 |

## 不装什么（同样重要）

- ❌ 各语言 `*-patterns` 知识类技能——模型本来就会，纯噪音
- ❌ 163 个全家桶式安装——按需挑选，上下文越干净 agent 越聪明
- ❌ 依赖未配置的 MCP/外部服务的技能——装了也是死件
