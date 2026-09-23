from pydantic import BaseModel,Field

class Briefing(BaseModel):
    topic: str =Field(description="本次简报的主题/搜索关键词")
    title: str =Field(description="简报标题")
    summary: str =Field(description="核心摘要，3-5句话")
    key_points: list[str] =Field(description="关键要点列表")
    sources: list[str] =Field(description="信息来源链接列表")

    