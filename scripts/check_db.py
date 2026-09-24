import asyncio

from sqlalchemy import select

from pdd_ai_coach.db import SessionLocal
from pdd_ai_coach.models import RuleRow


async def main() -> None:
    async with SessionLocal() as session:
        result = await session.execute(select(RuleRow))
        for rule in result.scalars():
            print(rule.number, rule.title)


asyncio.run(main())
