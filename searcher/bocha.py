import os
import requests
from dotenv import load_dotenv
import sys
from searcher import Searcher,create_searcher

load_dotenv()

BOCHA_API_KEY = os.environ.get("BOCHA_API_KEY")
BOCHA_API_URL = "https://api.bocha.cn/v1/web-search"


class BochaSearcher(Searcher):
    def search(self,query: str, count: int = 5, freshness: str = "noLimit" ) -> dict:
        """调用博查 Web Seacrch Api，返回原始json。"""
        headers = {
        "Authorization":f"Bearer {BOCHA_API_KEY}",
        "Content-Type":"application/json",
    }

        payload = {
        "query": query,
        "count": count,
        "freshness": freshness,
    }

        resp = requests.post(BOCHA_API_URL, headers=headers, json=payload)

        if resp.status_code != 200:
            raise RuntimeError(f"博查 API HTTP 地址错误{resp.status_code}:{resp.text}")

        data = resp.json()

        if data.get("code") != 200:
            raise RuntimeError(f"博查 API 业务错误:code={data.get('code')},message={data.get('message')}")

        return data


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python searcher/bocha.py <搜索关键词>")
        sys.exit(1)

    keywords = " ".join(sys.argv[1:])
    searcher = create_searcher("bocha")
    result = searcher.search(keywords)
    pages = result["data"]["webPages"]["value"]


    for i,page in enumerate(pages[:3],1):
        print(f"{i}.{page['name']}")
        print(f"   {page['url']}")
        print(f"   {page['snippet'][:60]}")
        print()
