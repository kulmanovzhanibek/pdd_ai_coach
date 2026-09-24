import asyncio

from openai import AsyncOpenAI
from sqlalchemy import select

from pdd_ai_coach.config import settings
from pdd_ai_coach.db import SessionLocal, engine
from pdd_ai_coach.models import RuleChunk

MODEL = "text-embedding-3-small"
BATCH_SIZE = 50

client = AsyncOpenAI(api_key=settings.openai_api_key)

async def main() -> None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(RuleChunk).where(RuleChunk.embedding.is_(None)).order_by(RuleChunk.id)
        ) 

        chunks = list(result.scalars())
        print("пунктов без эмбеддинга:", len(chunks))

        total_tokens = 0

        for start in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[start : start + BATCH_SIZE]
            response = await client.embeddings.create(
                model=MODEL,
                input=[chunk.text for chunk in batch]
            )
            for chunk, item in zip(batch, response.data, strict=True):
                chunk.embedding = item.embedding

            await session.commit()

            total_tokens += response.usage.total_tokens
            print(f"готово {start + len(batch)} из {len(chunks)}")  

    await engine.dispose()
    print("токенов всего:", total_tokens)        


asyncio.run(main())