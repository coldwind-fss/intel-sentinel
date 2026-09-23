# 情报哨兵项目 · 进度交接文档(HANDOFF)

> 用途:新开会话时,把本文档内容粘贴给新助手,说明"继续按此进度教学"。
> 最后更新:进行中(见"当前进度"节)。

## 一、学习方式约定(最重要,必须遵守)

- 用户要的是:**项目驱动学习**——通过开发"情报哨兵"项目学习 LangChain 全部核心知识点。
- **助手绝不代写代码文件**;用户在 VS Code 自己手敲,助手在对话区"一步一步教":这一步写什么、为什么、涉及什么知识点。
- 节奏:每个里程碑 = 助手拆步骤 → 用户写代码 → 贴结果/报错 → 助手验收 → 下一步。
- 教学格式模板:见 `D:\AI code dev\deepseek_harness_dev\lesson-format.md`(用户认可的固定结构:进度定位/文档原文/逐行拆解/关键点表格/运行机制图/动手任务/自检问题)。
- 用户明确反感:跳步、替写代码、省略文档原文、临场发挥加戏。主线 = 官网 docs 顺序。

## 二、项目定义

- 产品名:**情报哨兵**(自动化行业情报监测 Agent)
- 一句话:用户配置若干关注主题,Agent 调用联网搜索,生成结构化 Markdown 情报简报;简报入库后支持自然语言追问历史情报。
- 已拍板决策:
  1. 简报形态:Markdown 文件(存 `reports/`)
  2. 数据源:**博查搜索 API(Web Search)**,已购 key;**排除 RSS**(与产品设计冲突);搜索层做"接口抽象"预留扩展口(未来可加 Tavily/MCP)
  3. 定时运行:**后置**,先手动运行跑通全流程
  4. 模型:**DeepSeek(`deepseek:deepseek-chat`)**,API key 已配置
- 环境:.venv 位于 `D:\AI code dev\deepseek_harness_dev\langchain_dev\.venv`(Python 3.14.7);已装 langchain 1.3.15、langchain-deepseek 1.1.0、python-dotenv、requests
- `.env` 文件:`D:\AI code dev\deepseek_harness_dev\langchain_dev\.env`,含 `DEEPSEEK_API_KEY` 和 `BOCHA_API_KEY`

## 三、知识点地图(项目要覆盖的)

**A. LangChain 层(主干)**
- 必学:①模型(init_chat_model/provider:model/temperature/tool calling)②工具(@tool/docstring/args_schema)③agent(create_agent/agent loop/messages/content_blocks)④提示词(结构化 system_prompt/行为约束)⑤结构化输出
- 重要:⑥中间件 middleware ⑦短期记忆(State)+checkpointer+thread_id ⑧流式 streaming ⑨RAG ⑩ToolRuntime
- 进阶:⑪多智能体 ⑫长期记忆(Store);了解:⑬human-in-the-loop、MCP

**B. LangGraph 层**:①Graph API 基本概念(懂即可)②checkpointer 持久化 ③流式 ④interrupts
**C. Deep Agents 层**:①create_deep_agent 全家桶/虚拟文件系统 ②子代理/规划

## 四、里程碑(M1-M7,每步可运行)

| 里程碑 | 内容 | 勾掉知识点 | 验收 |
|---|---|---|---|
| M1 | 博查 API → searcher/bocha.py + 接口抽象 | 工具封装/API 调用/错误处理 | 命令行输关键词,打印搜索结果 |
| M2 | create_agent + 搜索工具 + 提示词 | 模型/agent/agent loop | 问"帮我搜 X"返回带链接答案 |
| M3 | 结构化输出:简报 schema | 结构化输出/提示词进阶 | 输出简报结构,非散文 |
| M4 | 简报落盘 Markdown + 多主题循环 | 文件工具/config 设计 | 3 主题 → reports/ 出 1 份 md |
| M5 | 记忆+追问:简报入库+检索回答 | 短期记忆/checkpointer/RAG | 追问"上次 X 说了什么"带来源 |
| M6 | 流式输出+中间件 | 流式/重试限流 | 打字机效果,失败自动重试 |
| M7(扩展位) | 子代理分工/长期记忆/MCP | 多智能体/Store/MCP | 任选其一 |

## 五、技术架构(已定)

```
入口层 main.py → Agent 层 create_agent(DeepSeek+工具+提示词) → 工具层 tools/ → 搜索层 searcher/
核心设计:searcher 定义统一接口(Searcher),BochaSearcher 是实现;换 provider 不改 agent 代码
```

## 六、文件目录(计划,按里程碑逐步创建,不全建)

```
langchain_dev/
├── .env                # ✅ 已有(DEEPSEEK_API_KEY、BOCHA_API_KEY)
├── requirements.txt    # 依赖清单(随装随加)
├── config.py           # 主题列表、简报输出目录(M4 出现)
├── searcher/
│   ├── __init__.py     # 导出接口+工厂
│   └── bocha.py        # 博查实现(M1 建)
├── tools/
│   ├── __init__.py
│   └── search.py       # @tool 封装(M2 建)
├── agent/
│   ├── __init__.py
│   └── build.py        # create_agent 组装(M2 建)
├── reports/            # 简报输出目录(M4 建)
├── test_bocha.py       # M1 临时验证脚本(进行中)
└── main.py             # 入口(M4 建)
```

## 七、当前进度(精确位置)

**阶段:M1(搜索层)第 1 步——写最小验证脚本 `test_bocha.py`**

已完成的准备:
- ✅ 博查 API 文档已带读(端点 `POST https://api.bocha.cn/v1/web-search`;Header: `Authorization: Bearer {KEY}` + `Content-Type: application/json`;Body: `{"query":必填, "count":1-50, "freshness":"noLimit|oneDay|oneWeek|oneMonth|oneYear", "summary":bool, "include"/"exclude":域名}`)
- ✅ 响应结构已讲:数据在 `data["data"]["webPages"]["value"]`,每条含 `name/url/snippet/summary/siteName/datePublished`
- ✅ 错误码已讲:400 缺参/key 缺失、401 key 无效、403 余额不足、429 频率超限、500 服务错误
- ✅ 用户已确认:建 `searcher/` 文件夹 + `__init__.py` + `.env` 加 BOCHA_API_KEY(用户自述"已买 key")

**正在做(助手已给出逐行代码,用户尚未运行/贴结果):**

文件 `test_bocha.py`,三段代码:
1. 导入+加载 .env:`import os` / `import requests` / `from dotenv import load_dotenv` / `load_dotenv()`
2. 发请求:`resp = requests.post("https://api.bocha.cn/v1/web-search", headers={"Authorization": f"Bearer {os.environ['BOCHA_API_KEY']}", "Content-Type": "application/json"}, json={"query": "LangChain 最新发布", "count": 5, "freshness": "oneWeek"})`
3. 打印:`data = resp.json()`;print HTTP/code/msg;`for page in data["data"]["webPages"]["value"][:3]:` 打印 name/url/snippet[:60]

前置:确认 `pip install requests` 已执行。

## 八、下一步(新会话接续点)

1. 用户运行 `python test_bocha.py`,贴输出 → 验收 M1 第 1 步
2. M1 第 2 步:把裸调用整理进 `searcher/bocha.py`(封装成函数 + 错误处理 + 接口抽象),逐行带教
3. M1 验收:M1 完成后命令行输入关键词能打印搜索结果
4. 进 M2:create_agent 接入搜索工具

## 九、环境速查

- 终端进入项目:`cd "D:\AI code dev\deepseek_harness_dev\langchain_dev"` + `.venv\Scripts\Activate.ps1`
- 模型:DeepSeek `deepseek:deepseek-chat`(注意:reasoner 不支持工具调用,不能用)
- 博查 key 平台:https://open.bocha.cn(免费资源包;429 是频率超限,403 是余额不足)
