from agent.schema import Briefing


def briefing_to_markdown(briefing: Briefing) -> str:
    key_points = "\n".join(f"- {point}" for point in briefing.key_points)
    sources = "\n".join(f"- {source}" for source in briefing.sources)

    return f"""# {briefing.title}

**主体**：{briefing.topic}

## 摘要

{briefing.summary}

## 关键要点

{key_points}

## 来源

{sources}
"""

