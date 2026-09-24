import asyncio

from sqlalchemy import select

from pdd_ai_coach.db import SessionLocal, engine
from pdd_ai_coach.llm import embed
from pdd_ai_coach.models import RuleChunk, RuleRow

QUESTION = "что такое опережение"


async def main() -> None:
    query_vector = await embed(QUESTION)
    distance = RuleChunk.embedding.cosine_distance(query_vector)

    stmt = (
        select(RuleRow.number, RuleChunk.text, distance)
        .join(RuleChunk, RuleChunk.rule_id == RuleRow.id)
        .order_by(distance)
        .limit(40)
    )

    async with SessionLocal() as session:
        rows = (await session.execute(stmt)).all()
    await engine.dispose()

    for place, (number, text, dist) in enumerate(rows, start=1):
        print(f"{place:>2}. п.{number:<5} {1 - dist:.3f}  {text.split("понятия:")[-1][:70]}")


asyncio.run(main())