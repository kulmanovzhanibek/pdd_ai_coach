import asyncio

from openai import AsyncOpenAI

from pdd_ai_coach.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

async def main() -> None:
    response = await client.embeddings.create(
         model="text-embedding-3-small",
        input="Можно ли обгонять на мосту?",
    )
    vector = response.data[0].embedding
    print("длина вектора:", len(vector))
    print("первые 5 чисел:", vector[:5])
    print("токенов:", response.usage.total_tokens)

asyncio.run(main())    
    