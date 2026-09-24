# 情报哨兵 · 全量项目上下文与演进记录

> 本文件是给后续接手本仓库的 Agent、开发者和教学助手使用的历史上下文说明。它不是一份重新搭建项目的计划，而是对项目从选题、设计、实现、教学、迁移、报错、验收到当前状态的连续记录。
>
> 使用方式：先阅读本文件了解“项目是怎么来的”，再阅读 `docs/PRODUCT_BASELINE.md` 了解当前确认的产品/技术基线，最后检查 Git 状态和实际代码。代码、测试输出和 Git 历史优先于本文中任何过时描述。
>
> 项目名称：情报哨兵（Intel Sentinel）
>
> 当前项目根目录：`D:\AI code dev\deepseek_harness_dev\情报哨兵`
>
> 目标 GitHub 仓库（私有）：`https://github.com/coldwind-fss/intel-sentinel.git`
>
> 文档创建时间：2026-09-24

---

## 0. 给接手 Agent 的最短结论

这是一个“项目驱动学习 LangChain”的真实小项目，不是让 Agent 代写完成的代码样例。用户自己在 VS Code 中手敲代码，助手只在对话中拆出一个最小步骤、解释原因、给出命令，然后等待用户贴运行结果。

产品是自动化行业情报监测 Agent：用户配置主题，系统调用博查搜索，交给 DeepSeek 摘要并生成结构化 Markdown 简报，后续把简报入库并支持历史追问。

M1、M2、M3 已完成并有验收记录。当前处于 M4：配置、报告目录和 Markdown 转换已完成；报告写入、入口编排、多主题循环和最终 3 主题验收尚未完成。

接手时不得重新搭建、不得回退 M1～M3、不得重复调用付费 API 以“确认状态”。首次只检查当前代码和 Git 状态，然后继续 M4 的一个最小步骤：在 `main.py` 中增加并验收报告写入函数。

---

## 1. 项目为什么会产生

### 1.1 学习目标

用户希望通过一个真实、可持续扩展的项目学习 LangChain，而不是先把所有概念讲完再做练习。项目必须让每个里程碑都能运行，让知识点在真正需要时出现。

最初的学习目标覆盖：

- LangChain 模型初始化和 provider:model 写法。
- 工具定义、参数 schema、工具调用。
- `create_agent`、Agent Loop、messages、content blocks。
- system prompt 与行为约束。
- 结构化输出。
- LangGraph 状态、checkpointer、thread_id、流式和 interrupts。
- 中间件、重试、限流、ToolRuntime。
- RAG、短期记忆、长期 Store。
- 多智能体、子代理、MCP、human-in-the-loop 的理解或扩展。
- Deep Agents 的规划、虚拟文件系统和子代理能力（作为额外知识地图）。

### 1.2 选题过程

项目从“选择一个能覆盖最多 LangChain 主干知识的项目”开始。曾讨论过多个方向，最后选定“自动化行业情报监测 Agent”，因为它天然包含真实数据源、工具调用、摘要、结构化输出、文件落盘、记忆和检索等连续链路。

这个选题不是为了做一个生产级新闻产品，而是让每个功能都对应一个 LangChain 学习节点，并且每个节点都能形成可运行的最小版本。

---

## 2. 产品定义的完整演进

### 2.1 产品定位

情报哨兵的正式定义：

> 用户配置若干关注主题，Agent 定时或手动抓取互联网信息，去重、摘要，生成结构化简报；简报落盘或入库，用户可以用自然语言追问历史情报。

当前阶段先做手动运行；自动定时运行明确后置。

### 2.2 核心场景

| 编号 | 场景 | 用户行为 | 系统行为 |
|---|---|---|---|
| S1 | 每日简报 | 配置主题“LangChain” | 搜索、摘要、输出标题/摘要/要点/来源 |
| S2 | 历史追问 | 问“最近 LangChain 的 RAG 有什么新特性？” | 从历史简报中检索并带来源回答 |
| S3 | 多轮对话 | 继续问“那和 Graph API 比呢？” | 记住上一轮上下文并理解指代 |
| S4 | 多主题 | 配置 3 个或更多主题 | 分别搜索，合并成一份简报 |
| S5 | 进阶分工 | 要求 Agent 拆任务 | 子代理分工、并行抓取或长期保存主题 |

### 2.3 产品形态

- 输入：`config.py` 中的主题列表。
- 搜索：博查 Web Search API。
- 推理和整理：DeepSeek `deepseek:deepseek-chat`。
- 输出：`Briefing` Pydantic 结构，随后转成 Markdown。
- 文件：Markdown 简报存放在 `reports/`。
- 交互：当前是命令行；没有 Web 前端。
- 后续：M5 再做入库、检索和追问。

### 2.4 明确排除项

以下内容在学习项目阶段不进入主线：

- RSS：它与“全网主动监测”的产品设计不一致。
- 自研爬虫：维护脆弱，搜索 API 更适合让模型消费。
- 模型服务端内置搜索：DeepSeek 没有本项目需要的内置 WebSearch。
- 自动定时调度：先把手动全流程跑通。
- Web/前端界面：先完成 CLI 后端核心。
- 多用户和权限。
- 生产级部署、日志、监控和高可用。

---

## 3. 数据源选择的来龙去脉

### 3.1 讨论过的搜索方式

| 方式 | 讨论结论 |
|---|---|
| 模型服务端内置搜索 | Claude/ChatGPT 等有内置能力，但当前 DeepSeek 没有，排除 |
| 搜索 API | Tavily、Exa、Bocha、SerpAPI 等，适合 AI 消费，是主线方案 |
| 自研爬虫 | 脆弱且维护成本高，不作为主线 |
| MCP 搜索封装 | 本质是搜索能力的包装盒，留作后期扩展 |
| RSS | 与全网主动监测设计冲突，明确排除 |

### 3.2 最终选择博查

最终选择博查（Bocha）的原因：

- 国内网络直连较方便。
- 中文搜索效果符合当前项目。
- 一次调用返回结构化标题、链接、摘要，方便交给模型。
- 用户已有可用的博查 Key。
- 通过 `Searcher` 接口抽象后，未来更换 Tavily 或 MCP 不需要重写 Agent。

### 3.3 博查 API 事实

已带教并在早期验证中使用过：

- Endpoint：`POST https://api.bocha.cn/v1/web-search`
- Header：`Authorization: Bearer {KEY}`、`Content-Type: application/json`
- Body 主要字段：`query`、`count`、`freshness`，可扩展 `summary`、`include`、`exclude`。
- `count` 约定为 1～50。
- `freshness` 支持 `noLimit`、`oneDay`、`oneWeek`、`oneMonth`、`oneYear`。
- 结果主要位于 `data["data"]["webPages"]["value"]`。
- 每条结果包含或可能包含 `name`、`url`、`snippet`、`summary`、`siteName`、`datePublished`。

早期讲过的常见错误：400 参数或 Key 缺失、401 Key 无效、403 博查余额不足、429 频率超限、500 服务错误。实际项目代码同时检查 HTTP 状态和业务 `code`。

---

## 4. 项目架构是如何确定的

### 4.1 最终单向依赖

```text
用户配置主题
    ↓
main.py（入口和编排）
    ↓
agent/build.py（DeepSeek + Agent + 提示词 + 结构化输出）
    ↓
tools/search.py（LangChain @tool）
    ↓
searcher/__init__.py（Searcher 接口 + 工厂）
    ↓
searcher/bocha.py（BochaSearcher + HTTP API）
```

核心约束：Agent 不直接知道博查 HTTP 细节；工具不直接写 provider 选择逻辑；provider 更换只影响 `searcher/`。

### 4.2 规划中的文件树

```text
情报哨兵/
├── .env                 # 本地密钥，不进 Git
├── .gitignore           # 已建立，排除密钥、虚拟环境和缓存
├── docs/
│   ├── PRODUCT_BASELINE.md  # 当前产品/技术基线
│   └── PROJECT_CONTEXT.md   # 本文件，完整历史上下文
├── config.py            # M4：主题和输出目录
├── searcher/
│   ├── __init__.py      # Searcher 接口和 create_searcher 工厂
│   └── bocha.py         # BochaSearcher 实现
├── tools/
│   ├── __init__.py
│   └── search.py        # @tool search_web
├── agent/
│   ├── __init__.py
│   ├── schema.py        # Briefing Pydantic schema
│   └── build.py         # create_agent 组装
├── reports/
│   └── .gitkeep         # 保留空目录；以后放 Markdown 简报
├── main.py              # M4 入口、Markdown 和文件写入
├── 测试1.py             # 工作区中已有的历史测试脚本，作用待核实
└── PROJECT_BRIEF.md     # 早期交接稿，内容过时，仅作历史资料
```

### 4.3 当前真实依赖方向

- `agent/build.py` 导入 `tools.search.search_web` 和 `agent.schema.Briefing`。
- `tools/search.py` 通过 `create_searcher("bocha")` 使用搜索层。
- `searcher/bocha.py` 读取 `BOCHA_API_KEY`，调用博查并返回原始 JSON。
- `main.py` 当前已能把 `Briefing` 转成 Markdown 字符串，但尚未在当前实际文件中完成保存函数和入口。

---

## 5. 里程碑历史与实现细节

### M1：博查 API 与搜索层底座

#### M1 目标

先把真实数据源跑通，再让后续 Agent 使用真实搜索结果。知识点是 HTTP API、错误处理、工具底座和接口抽象。

#### M1 早期裸调用教学

早期曾规划一个临时 `test_bocha.py`，内容分为三段：

1. `os`、`requests`、`load_dotenv()` 导入和环境加载。
2. 使用 `requests.post()` 调博查 endpoint，传入 Bearer Key、JSON body、查询词、数量和 freshness。
3. 打印 HTTP 状态、业务 code/message，并遍历前三条 `webPages.value` 输出标题、链接和摘要。

这一阶段的意义是先理解 API 原始响应，而不是马上隐藏在类和 Agent 里。

#### M1 正式实现

随后将裸调用整理成：

- `Searcher(ABC)` 抽象接口。
- `BochaSearcher(Searcher)` 实现。
- `create_searcher(source="bocha")` 工厂。
- `searcher.bocha` 的 CLI 入口，支持 `python -m searcher.bocha <关键词>`。

`BochaSearcher.search()` 负责：

1. 从环境变量取得 `BOCHA_API_KEY`。
2. 构造请求 header 和 payload。
3. 发起 POST 请求。
4. 检查 HTTP 状态码。
5. 解析 JSON 并检查业务 `code`。
6. 返回原始搜索 JSON，让上层决定如何格式化。

#### M1 验收

历史验收记录为：

```powershell
python -m searcher.bocha LangChain 最新发布
```

可以打印前 3 条标题、链接和摘要。该结果被视为 M1 完成。

---

### M2：Agent 接入搜索工具

#### M2 目标

让 DeepSeek 能通过 LangChain Agent 自主决定调用搜索工具，并返回带来源的回答。知识点是模型、工具、Agent Loop、messages 和分层依赖。

#### M2 实现

- `tools/search.py` 使用 `from langchain_core.tools import tool`。
- `search_web()` 加 `@tool`，输入 `query`、`count`、`freshness`。
- 工具内部调用 `create_searcher("bocha")`，把搜索 JSON 格式化成标题、链接和摘要文本。
- `agent/build.py` 使用 `init_chat_model("deepseek:deepseek-chat", temperature=0)`。
- 使用 `create_agent(model=model, tools=[search_web], system_prompt=...)`。
- 入口通过 `agent.invoke({"messages": [...]})` 发送用户消息。

#### M2 验收

历史验收命令：

```powershell
python -m agent.build
```

可以返回带链接的 Markdown 回答。M2 之后复习过 `@tool`、`invoke`、`init_chat_model`、`create_agent`、Agent Loop、`messages` 和分层架构。

---

### M3：结构化简报输出

#### M3 目标

让 Agent 的输出不再是不可控的散文，而是可被程序继续处理的 `Briefing` 数据。知识点是 Pydantic schema、结构化输出、提示词约束和 provider 兼容性。

#### M3 schema

当前 `agent/schema.py` 的设计为：

```python
from pydantic import BaseModel, Field


class Briefing(BaseModel):
    topic: str = Field(description="本次简报的主题/搜索关键词")
    title: str = Field(description="简报标题")
    summary: str = Field(description="核心摘要，3-5句话")
    key_points: list[str] = Field(description="关键要点列表")
    sources: list[str] = Field(description="信息来源链接列表")
```

当前实际文件的空格格式略有差异，但字段语义相同。

#### M3 遇到的问题

最初尝试 `create_agent(response_format=Briefing)` 时发现：

- DeepSeek 不支持原生结构化输出。
- LangChain 会退回 ToolStrategy。
- 当 Agent 同时拥有 `search_web` 和结构化输出工具时，DeepSeek 可能一直调用 `search_web`。
- 结果可能超时、循环，或者没有 `structured_response`，随后访问 `result["structured_response"]` 会触发 `KeyError`。

#### M3 解决方案

用户确认继续使用中间件路线，不切换成两段式手动调用。当前 Agent 使用：

```python
response_format=Briefing
middleware=[
    ToolCallLimitMiddleware(
        tool_name="search_web",
        run_limit=1,
        exit_behavior="continue",
    )
]
```

系统提示词明确要求：先调用 `search_web`，搜索结束后必须调用 `Briefing`，不要继续搜索。

#### M3 运行问题流转

1. 第一次运行时使用了系统 Python，出现 `ModuleNotFoundError: No module named 'langchain'`。
2. 发现没有激活项目虚拟环境后，改为先运行 `.venv\Scripts\Activate.ps1`。
3. 进入虚拟环境后，模型请求到达 DeepSeek，但返回 HTTP 402：`Insufficient Balance`。
4. 余额问题处理后再次运行成功，返回结构化字典。

#### M3 成功输出形态

用户实际贴回的结果包含：

```text
topic
title
summary
key_points
sources
```

内容是 LangChain 最新发布相关简报；搜索结果主要来自中文社区/技术博客，模型明确说明没有找到足够权威的官方发布渠道，并给出来源链接。该次结果证明 `result["structured_response"]` 和 `briefing.model_dump()` 路径成功。

M3 因此完成验收。注意：这次实际调用的 DeepSeek/博查次数没有建立精确计数，不得在后续文档中虚构数字。

---

### M4：Markdown 落盘与多主题循环

#### M4 原定目标

把一次结构化 Agent 调用变成可保存、可批量运行的简报生产流程：配置主题、转 Markdown、保存文件、循环多个主题。

#### 已完成的 M4 小步骤

1. 在项目根目录建立 `config.py`。
2. 配置 `TOPICS` 和 `REPORTS_DIR`。
3. 创建 `reports/` 目录并验证存在。
4. 在 `main.py` 建立 `briefing_to_markdown(briefing)`。
5. 成功运行：

```powershell
python -c "from config import TOPICS, REPORTS_DIR; print(TOPICS); print(REPORTS_DIR)"
```

输出过：

```text
['Langchain 最新发布']
reports
```

6. 成功运行：

```powershell
python -c "from main import briefing_to_markdown; print('main 导入成功')"
```

#### M4 中出现的具体问题

- 配置文件第一次把 `TOPICS` 拼成 `TPPICS`，导致 `ImportError: cannot import name 'TOPICS'`；已由用户改正。
- 曾在 `C:\WINDOWS\system32` 执行 Python，导入到了错误的 `config` 环境；切换到项目根目录后解决。
- 曾创建成 `report` 单数，而配置定义的是 `reports` 复数；已重命名并通过 `Test-Path .\reports` 返回 `True`。
- 当前 `config.py` 使用的是 `Langchain 最新发布`，与产品文案中的 `LangChain 最新发布`大小写略不同；不阻塞运行，后续可统一。
- 当前 `main.py` 的 Markdown 标签写成了 `**主体**`，语义上应确认是否改为 `**主题**`。

#### M4 当前未完成部分

之前已经给过 `save_report()` 的教学片段，但在本次上下文审计中，当前实际 `main.py` 仍只有 Markdown 转换函数，没有 `save_report()`。因此不得把它写成已完成。

当前准确接续点：

1. 用户手敲并导入验收 `save_report()`。
2. 再让入口调用 `build_agent()`，取得 `structured_response` 并保存一份报告。
3. 再读取 `config.TOPICS` 做多主题循环。
4. 最后用 3 个主题生成 1 份 Markdown，完成 M4。

每个步骤都要用户运行并贴结果；不要一次把 M4 全部写完。

---

## 6. 教学协议的演进与优先级

### 6.1 早期 HANDOFF v4 约定

早期交接稿要求在固定教学格式中输出：

1. 进度定位。
2. 文档原文。
3. 逐行拆解。
4. 关键点表格。
5. 运行机制图。
6. 动手任务。
7. 自检问题。

这个完整格式只适合用户明确要求复习或讲透一个知识块时使用。

### 6.2 后续用户明确绑定的日常规则

后续用户明确要求日常开发回复尽量短，只保留：

1. 这一步做什么。
2. 要手敲的代码。
3. 为什么这么写（2～5 句话）。
4. 运行命令。
5. 停止等待用户输出。

这是当前优先规则。除非用户明确说“复习”“讲透”“进入复习模式”，不要贴完整教案、不要同时给表格/机制图/自检题。

### 6.3 不可协商的工作方式

- 用户在 VS Code 手敲代码，助手绝不直接编辑代码文件。
- 用户运行命令，助手不替用户运行 `python -m ...`。
- 用户贴完整结果后才验收；没有结果不能宣布通过。
- 每次只给一个最小可执行步骤。
- 不提前讲后续里程碑，不替用户决定未确认的产品范围。
- 遇到报错先读完整 traceback，只定位一个最可能问题。
- 如果是助手的设计遗漏，要直接承认，不让用户承担责任。
- 用户不喜欢为了教学而教学，不喜欢跳步、临场加戏和整文件重写。
- 语言使用中文；术语第一次出现只用一句话解释。
- 不重复触发付费模型或搜索 API 调用。

---

## 7. 环境与路径迁移记录

### 7.1 早期规划路径

早期文档和第一次交接稿中曾写 `langchain_dev` 作为项目目录，虚拟环境和 `.env` 也曾被描述在该路径下。

### 7.2 当前实际路径

开发过程中项目根目录改为：

```text
D:\AI code dev\deepseek_harness_dev\情报哨兵
```

当前虚拟环境为：

```text
D:\AI code dev\deepseek_harness_dev\情报哨兵\.venv
```

当前 `.env` 位于项目根目录，包含两个字段名：

- `DEEPSEEK_API_KEY`
- `BOCHA_API_KEY`

字段值永远不写入文档、聊天或 Git。

### 7.3 迁移判断

这里发生过“项目上下文从旧对话迁移到新对话”，但不是重新搭建产品。代码沿用当前工作区，M1～M3 的设计和已验收结果不能因为对话迁移而被重做。

---

## 8. 依赖和运行记录

### 8.1 已确认的依赖版本

当前虚拟环境曾确认：

- `langchain 1.3.15`
- `langchain-deepseek 1.1.0`
- `pydantic 2.13.4`
- `python-dotenv`
- `requests`

Python 版本曾记录为 3.14.7；如重新接手，应以当前 `.venv` 实际解释器为准，不要仅凭历史版本判断。

### 8.2 正确的运行方式

PowerShell 中：

```powershell
cd "D:\AI code dev\deepseek_harness_dev\情报哨兵"
.\.venv\Scripts\Activate.ps1
python -m searcher.bocha LangChain 最新发布
python -m tools.search
python -m agent.build
```

包内导入使用模块方式，不要从错误工作目录执行。特别是不能在 `C:\WINDOWS\system32` 运行项目导入测试。

### 8.3 外部 API 调用纪律

- `python -m agent.build` 会调用 DeepSeek，并可能通过 Agent 调用博查。
- `python -m tools.search` 会直接触发博查。
- 没有必要时只做 import/config/path 检查，避免付费调用。
- 遇到余额、限流或网络错误，先记录完整错误，再决定是否需要用户处理外部状态。
- API 调用数量历史上未精确统计，后续只记录“是否调用”和结果，不要编造计数。

---

## 9. 当前文件事实快照

以下是本上下文文档创建时观察到的事实，不等同于未来代码一定保持不变：

| 文件/目录 | 当前事实 | 状态 |
|---|---|---|
| `agent/schema.py` | 定义 `Briefing` 五个字段 | M3 已验收 |
| `agent/build.py` | DeepSeek、`search_web`、`Briefing`、搜索调用限制中间件 | M3 已验收 |
| `tools/search.py` | `@tool search_web`，调用搜索工厂并格式化结果 | M2 已验收 |
| `searcher/__init__.py` | `Searcher` 抽象接口和 `create_searcher` | M1 已验收 |
| `searcher/bocha.py` | 博查 HTTP 实现、HTTP/业务错误检查、CLI | M1 已验收 |
| `config.py` | `TOPICS` 和 `REPORTS_DIR` | M4 部分完成 |
| `main.py` | `briefing_to_markdown`；当前实际文件没有 `save_report` | M4 进行中 |
| `reports/` | 目录存在，以 `.gitkeep` 保留 | M4 部分完成 |
| `PROJECT_BRIEF.md` | 早期 M1 交接稿，路径和进度过时 | 历史资料 |
| `docs/PRODUCT_BASELINE.md` | 当前产品/技术基线 | 权威基线 |
| `.gitignore` | 排除 `.env`、`.venv`、缓存 | Git 安全规则 |
| `requirements.txt` | 尚未建立 | 待办 |
| `测试1.py` | 工作区已有历史测试脚本 | 作用待核实 |

### 9.1 不要误把意图当成代码

产品蓝图中写有“main.py 负责写报告和多主题循环”，但这不是当前事实；当前 `main.py` 只确认了 Markdown 转换函数。任何 Agent 接手时都必须以实际文件为准，逐步实现剩余部分。

---

## 10. Git 与 GitHub 演进记录

### 10.1 首次本地 Git 同步

在第一次要求将项目和需求文档同步到 GitHub 时，发现工作区原本不是 Git 仓库，也没有 `.gitignore`。随后完成：

1. 初始化本地 Git，分支为 `main`。
2. 创建 `.gitignore`，排除 `.env`、`.venv/`、`__pycache__/`、`.pyc` 和本地编辑器目录。
3. 建立 `docs/PRODUCT_BASELINE.md`。
4. 用当前工作区代码和文档建立首次提交。
5. 添加远程 `origin`：`https://github.com/coldwind-fss/intel-sentinel.git`。
6. 推送 `main` 到私有 GitHub 仓库。

首次提交信息：

```text
b69f28a docs: add project baseline and teaching guide
```

### 10.2 当前同步纪律

- 本仓库是私有仓库，但私有不等于可以提交密钥。
- `.env` 永远不应出现在 `git status` 的待提交文件里。
- 推送前检查当前分支、远程 URL、暂存文件和工作树。
- 不用 `git reset --hard` 或 `git checkout --` 回退用户代码。
- 本文件的新增提交应保留在 `main`，并推送到 `origin/main`。
- 如果未来远程出现与本地不同的提交，不要盲目强推，先报告分叉状态。

---

## 11. 已知风险、未决事项和不要重复踩的坑

### 11.1 已知风险

- DeepSeek 结构化输出不稳定，必须保留 `Briefing` 工具策略和搜索调用限制，直到有新的已验证方案。
- 外部 API 有余额和频率限制，不能频繁运行验证命令。
- 没有 `requirements.txt`，换机器时依赖再现性不足。
- `main.py` 尚未形成完整入口，不能把 M4 写成已完成。
- `sources` 当前模型输出可能是 Markdown 链接字符串，而不是纯 URL；schema 只要求 `list[str]`，是否统一格式属于后续实现决策。
- 早期 `PROJECT_BRIEF.md` 的路径和进度会误导新 Agent。

### 11.2 待决定但尚未拍板

- 报告文件名是按主题、时间戳，还是主题加时间戳。
- 多主题是每个主题一份文件，还是合并为一份文件；当前 M4 验收目标倾向于合并成一份。
- 是否在 M4 统一 `LangChain` 大小写和 Markdown 的“主题”标签。
- 是否建立 `requirements.txt`，以及由用户决定何时整理依赖。
- M5 采用哪种向量库/检索实现；当前只确认要做历史检索，不提前锁死具体库。
- M7 选择子代理、长期 Store 或 MCP 中的哪一个。

### 11.3 禁止的错误恢复方式

- 不因为新 Agent 不理解上下文就重写 M1～M3。
- 不把 `PROJECT_BRIEF.md` 里的旧 M1 状态当当前状态。
- 不直接运行多次 `python -m agent.build` 直到“碰巧成功”。
- 不把 API Key 贴到聊天里让助手检查。
- 不擅自把搜索源切成 RSS 或把 DeepSeek 改成 reasoner。
- 不为了完成文档而修改用户尚未要求的业务代码。

---

## 12. 给未来接手 Agent 的操作协议

### 12.1 首次检查顺序

在项目根目录执行只读检查：

```powershell
cd "D:\AI code dev\deepseek_harness_dev\情报哨兵"
git status --short --branch
git log --oneline --decorate -5
git remote -v
Get-Content .\docs\PRODUCT_BASELINE.md
Get-Content .\config.py
Get-Content .\main.py
```

不要先运行会调用外部 API 的命令。

### 12.2 接续原则

1. 先区分“已确认产品意图”和“当前代码事实”。
2. 先尊重用户的手敲教学模式。
3. 每次只给一个小任务。
4. 代码片段只覆盖当前任务，不贴整个文件。
5. 用户贴结果后再验收。
6. 发现文档与代码不一致时，报告差异，不要静默回退或重写。
7. 只有用户明确要求复习时，才使用完整复习格式。

### 12.3 当前第一件可做的事

当前未完成的最小任务是 `main.py` 的 `save_report()`：

- 先让用户手敲导入 `REPORTS_DIR` 和保存函数。
- 先做无 API 的导入检查。
- 再由用户决定是否运行真实 Agent 生成一份报告。
- 不要一次实现多主题循环。

---

## 13. 这份文件与其他文档的关系

| 文档 | 用途 | 权威范围 |
|---|---|---|
| `docs/PRODUCT_BASELINE.md` | 当前产品、技术、里程碑和教学基线 | 当前确认意图和当前状态 |
| `docs/PROJECT_CONTEXT.md` | 本文件，完整历史、问题流转和迁移背景 | 上下文恢复和历史解释 |
| `PROJECT_BRIEF.md` | 早期交接稿 | 仅历史参考，不覆盖新基线 |
| `lesson-format.md`（项目外路径） | 早期完整复习教学格式 | 仅在用户明确要求复习时参考 |

如果后续确认了新的产品决策，应更新 `PRODUCT_BASELINE.md`；如果发生新的重大迁移、报错或教学规则变化，应在本文件追加带日期的上下文记录，并同步 Git。

---

## 14. 迁移时的最后核对清单

接手 Agent 应确认：

- [ ] 当前工作目录是 `D:\AI code dev\deepseek_harness_dev\情报哨兵`。
- [ ] 读取了 `docs/PRODUCT_BASELINE.md` 和本文件。
- [ ] Git 当前分支和远程状态已检查。
- [ ] `.env` 未被读取并输出，密钥未进入回复或提交。
- [ ] 没有重做 M1、M2、M3。
- [ ] 知道 M3 的 DeepSeek 结构化输出兼容性问题。
- [ ] 知道 M4 目前只完成到 Markdown 转换。
- [ ] 知道下一步是一个最小的 `save_report()` 任务。
- [ ] 知道用户需要自己手敲代码并贴运行结果。
- [ ] 没有为了验证而重复调用付费 API。

本文件的目标是让新 Agent 直接接上现有项目，而不是让新 Agent 重新猜测项目历史。

