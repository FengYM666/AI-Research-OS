---
name: paper-search
description: 查论文、找论文、文献调研、找 related work 时使用。只从权威学术来源检索（谷歌学术、Papers with Code、OpenAlex、arXiv、CVF/NeurIPS/ICML 等顶会官网、dblp、ACL Anthology），每篇论文必须核实真实存在再引用，禁止凭记忆编造。Use when searching for academic papers, doing literature review, or verifying citations.
---

# 论文检索规范（Paper Search）

用户主业是学术研究。帮他查论文时，准确性 > 数量 > 速度。

## 铁律：不许编造

1. 推荐的每篇论文必须来自**本轮实际检索到的真实记录**（API 响应或网页抓取内容），禁止凭训练记忆列论文——记忆里的人名、标题、年份极易张冠李戴。
2. 引用五要素必须齐全且出自**同一条真实记录**：标题、作者、年份、发表 venue、可访问链接。
3. 查不到就明说"没查到"；只凭印象但没能核实的，标注【未核实】并说明。
4. 给出实际使用的检索式，让用户可以复现和继续深挖。
5. 注意区分正式发表版本和 arXiv 预印本；两者标题相同优先引用正式发表信息。

## 首选工具：paper-search MCP（已配置）

ZCode 已接入 `paper-search` MCP 服务器（openags/paper-search-mcp，57 个工具）。**检索优先调用它的工具**，不用自己 curl：

- `search_papers`（跨库统一检索）、`search_arxiv`、`search_openalex`、`search_dblp`、`search_semantic`、`search_google_scholar`、`search_crossref` 等 20 个源的检索
- `download_arxiv` / `read_arxiv_paper` 等：下 PDF、抽正文（每个源都有对应工具）
- Google Scholar 检索已配好梯子代理（PAPER_SEARCH_MCP_GOOGLE_SCHOLAR_PROXY_URL）；梯子没开时 GS 会失败，换其它源即可

MCP 不可用时（比如服务器没连上），退回到下面手动 curl 的路子。

## 来源与连通性（2026-09 在本机实测）

**直连可用（终端无需代理）：**

| 来源 | 用途 | 入口 |
|---|---|---|
| OpenAlex API | **首选**：免费无 key，覆盖 2.5 亿+ 论文，可按日期/venue/被引过滤 | `https://api.openalex.org/works?search=<词>&per-page=10`，加 `&filter=from_publication_date:YYYY-01-01` 限定年份 |
| arXiv API | 预印本，CV/AI 新论文首发地 | `https://export.arxiv.org/api/query?search_query=all:<词>&max_results=10&sortBy=submittedDate` |
| CVF Open Access | CVPR / ICCV / ECCV **官方全文**，含 workshop | openaccess.thecvf.com |
| dblp API | **验证**论文真实发表 venue 和年份的金标准 | `https://dblp.org/search/publ/api?q=<标题>&format=json` |
| Papers with Code | 论文 + 官方代码 + SOTA 榜单 | paperswithcode.com |
| 领域官方库 | ACL Anthology（NLP）、proceedings.neurips.cc、proceedings.mlr.press（ICML）、OpenReview（ICLR） | 各自官网 |

**需要梯子（终端先 `export https_proxy=http://127.0.0.1:7890`，端口以你的代理软件为准）：**

| 来源 | 用途 | 注意 |
|---|---|---|
| 谷歌学术 | 覆盖最广、被引量、引文追踪、"相关文章"扩展 | **优先用 control-browser 技能开真实浏览器搜**（系统代理自动生效、能过人机验证）；curl 抓取容易触发 CAPTCHA |
| Semantic Scholar API | 引用网络分析、TLDR 摘要 | 无 key 限流严重（易 429），少量请求可用，做备用 |

## 工作流

1. **拆检索式**：把用户需求拆成 2~4 个英文检索式（学术库基本只认英文；中文需求先翻译关键词）。
2. **初筛**：OpenAlex + arXiv 检索，按相关性、年份、被引量挑候选。
3. **核实 venue**：声称发表在 CVPR/ICCV 等会的，用 dblp 或会议官网核对——这一步专治"看起来很真的假论文"。
4. **找代码/SOTA**：Papers with Code。
5. **扩展经典**：谷歌学术按被引排序 + "相关文章" + 顺藤摸瓜参考文献。
6. **输出前逐条过一遍五要素**，缺一项就回去补查。

## 输出格式

| 标题 | 作者 | 会议/期刊 + 年份 | 链接 | 与需求的关系（一句话） |
|---|---|---|---|---|

表后附：本次用到的检索式；有官方代码的附代码库链接；说明哪些条目没来得及核实。
