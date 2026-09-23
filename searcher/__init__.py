from abc import ABC,abstractmethod

class Searcher(ABC):
    """搜索接口，所有数据源都统一用这一套接口标准"""

    @abstractmethod
    def search(
        self,
        query:str,
        count:int=5,
        freshness:str="noLimit",
        )-> dict:
        """根据关键词返回原始搜索结果 JSON。"""


def create_searcher(source: str = "bocha") -> Searcher:
    """根据名称创建对应的搜索实现"""
    if source == "bocha":
        from searcher.bocha import BochaSearcher
        return BochaSearcher()
    raise ValueError(f"未知搜索源:{source}")
