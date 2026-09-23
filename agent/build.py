from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from tools.search import search_web
from dotenv import load_dotenv
from agent.schema import Briefing
from langchain.agents.middleware.tool_call_limit import ToolCallLimitMiddleware

load_dotenv()

def build_agent():
    """创建情报哨兵 Agent。"""
    model = init_chat_model(
        "deepseek:deepseek-chat",
        temperature = 0,

    )

    SYSTEM_PROMPT = ("你是一个情报搜索助手。先调用 search_web 获取搜索结果；"
            "搜索完成后，必须调用 Briefing 工具提交最终结构化简报，不要继续调用 search_web。")

    agent = create_agent(
        model = model,

        tools = [search_web],

        system_prompt = SYSTEM_PROMPT,
        
        response_format=Briefing,

        middleware = [
        ToolCallLimitMiddleware(
            tool_name="search_web",
            run_limit=1,
            exit_behavior="continue",
            )
        ],
    )
    return agent



if __name__ == "__main__":
    agent = build_agent()
    result = agent.invoke({"messages":[{"role":"user","content":"帮我搜一下LangChain 最新发布"}]})

    briefing = result["structured_response"]
    print(briefing.model_dump())
    #print(result["messages"][-1].content)