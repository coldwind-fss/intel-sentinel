from langchain_core.tools import tool
from searcher import create_searcher

@tool
def search_web(query: str, count : int = 5,freshness: str = "noLimit") -> str:
    """搜索互联网并返回前几条结果的标题，链接和摘要。当用户需要最新消息或实时资料时使用。"""
    searcher = create_searcher("bocha")
    data = searcher.search(query,count=count, freshness=freshness)
    pages = data["data"]["webPages"]["value"]

    lines = []
    for i,page in enumerate(pages[:count], 1):
        lines.append(
            f"{i}. {page['name']}\n"
            f"   链接： {page['url']}\n"
            f"   摘要： {page['snippet'][:200]}"    
        )

    return "\n\n".join(lines)  

if __name__ == "__main__":
    print(search_web.invoke({"query":"LangChain 最新发布","count":3}))