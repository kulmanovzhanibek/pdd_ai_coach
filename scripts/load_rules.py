import asyncio
from dataclasses import asdict
from pathlib import Path

from sqlalchemy.dialects.postgresql import insert

from pdd_ai_coach.db import SessionLocal, engine
from pdd_ai_coach.models import RuleRow
from pdd_ai_coach.parser import parse_rules

RULES_PATH = Path("data/pdd_rules.txt")

async def main() -> None:
    lines = RULES_PATH.read_text(encoding="utf-8").splitlines()
    rules = parse_rules(lines)
    rows = [asdict(rule) for rule in rules]

    stmt = insert(RuleRow).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["number"],
        set_={
            "text": stmt.excluded.text,
            "chapter_number": stmt.excluded.chapter_number,
            "chapter_title": stmt.excluded.chapter_title,
            "note": stmt.excluded.note,
        }
    )

    async with SessionLocal() as session:
        await session.execute(stmt)
        await session.commit()

    await engine.dispose()
    print(f"загружено пунктов: {len(rows)}")    

asyncio.run(main())
