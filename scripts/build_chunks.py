import asyncio

from sqlalchemy import delete, select

from pdd_ai_coach.chunking import split_rule
from pdd_ai_coach.db import SessionLocal, engine
from pdd_ai_coach.models import RuleChunk, RuleRow


async def main() -> None:
    async with SessionLocal() as session:
        await session.execute(delete(RuleChunk))

        result = await session.execute(select(RuleRow).order_by(RuleRow.id))
        count = 0
        for rule in result.scalars():
            header = f"Глава {rule.chapter_number}. {rule.chapter_title}. Пункт {rule.number}."
            for position, part in enumerate(split_rule(rule.text)):
                session.add(RuleChunk(rule_id=rule.id, position=position, text=f"{header} {part}"))
                count += 1

        await session.commit()

    await engine.dispose()
    print("чанков:", count)


asyncio.run(main())