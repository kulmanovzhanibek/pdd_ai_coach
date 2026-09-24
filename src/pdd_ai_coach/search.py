from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pdd_ai_coach.llm import embed
from pdd_ai_coach.models import RuleChunk, RuleRow

DEFAULT_K = 8

@dataclass
class Hit:
    rule: RuleRow
    chunk_text: str
    score: float

async def retrieve(session: AsyncSession, question: str, k: int = DEFAULT_K) -> list[Hit]:
    query_vector = await embed(question)
    distance = RuleChunk.embedding.cosine_distance(query_vector)
    stmt = (
        select(RuleRow, RuleChunk.text, distance)
        .join(RuleChunk, RuleChunk.rule_id == RuleRow.id)
        .order_by(distance)
        .limit(k * 4)
    )
    rows = (await session.execute(stmt)).all()
    hits: list[Hit] = []
    seen: set[str] = set()

    for rule, chunk_text, dist in rows: 
        if rule.number in seen:
            continue
        seen.add(rule.number)
        
        hits.append(Hit(rule=rule, chunk_text=chunk_text, score=round(1 - dist, 3)))

        if len(hits) == k:
            break    
    return hits    