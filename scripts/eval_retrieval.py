import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pdd_ai_coach.db import SessionLocal, engine
from pdd_ai_coach.llm import embed
from pdd_ai_coach.models import RuleChunk, RuleRow

TOP_K = 8

CASES: list[tuple[str, set[str]]] = [
    ("что такое обгон", {"2"}),
    ("что такое опережение", {"2"}),
    ("когда включать аварийку", {"44"}),
    ("на каком расстоянии ставить знак аварийной остановки", {"45"}),
    ("можно ли говорить по телефону за рулём", {"12"}),
    ("где запрещен обгон", {"81"}),
    ("в чем убедиться перед обгоном", {"77"}),
    ("с какой стороны обгонять", {"78"}),
    ("где нельзя разворачиваться", {"58"}),
    ("как предупредить об обгоне светом фар", {"140"}),
    ("можно ли ехать по трамвайным путям", {"65"}),
    ("машина заглохла на железнодорожном переезде что делать", {"117"}),
    ("Сколько секунд еще у меня есть после того как зеленый погаснет, чтобы сделать последний маневр?", {"24", "37"}),
    ("Могу ли я брать разворот после светофора где хочу?", {"55", "58", "61"}),
    ("Как правильно держать полосы при развороте на кольцевой?", {"52"}),
    ("Кто прав если спереди резко тормознули, машина тоже нажала на тормоз, а сзади машина врезалась в него?", {"69", "76"}),
]


async def search_numbers(session: AsyncSession, question: str) -> list[str]:
    vector = await embed(question)
    distance = RuleChunk.embedding.cosine_distance(vector)
    stmt = (
        select(RuleRow.number)
        .join(RuleChunk, RuleChunk.rule_id == RuleRow.id)
        .order_by(distance)
        .limit(40)
    )
    numbers: list[str] = []
    for number in (await session.execute(stmt)).scalars():
        if number not in numbers:
            numbers.append(number)
        if len(numbers) == TOP_K:
            break
    return numbers


async def main() -> None:
    hits = 0
    async with SessionLocal() as session:
        for question, expected in CASES:
            found = await search_numbers(session, question)
            places = [found.index(n) + 1 for n in expected if n in found]
            ok = bool(places)
            hits += ok
            mark = "✓" if ok else "✗"
            place = min(places) if places else "-"
            wanted = ",".join(sorted(expected))
            print(f"{mark} {question[:45]:<45} ждём {wanted:<8} место {place}  {found}")
    await engine.dispose()
    print(f"\nhit@{TOP_K}: {hits}/{len(CASES)}")


asyncio.run(main())