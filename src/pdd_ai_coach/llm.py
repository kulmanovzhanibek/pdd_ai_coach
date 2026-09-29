from openai import AsyncOpenAI
from pydantic import BaseModel

from pdd_ai_coach.config import settings

EMBEDDING_MODEL = "text-embedding-3-small"

openai_client = AsyncOpenAI(api_key=settings.openai_api_key)


async def embed(text: str) -> list[float]:
    response = await openai_client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding

SYSTEM_PROMPT = """Ты ассистент по Правилам дорожного движения Республики Казахстан.

Правила ответа:
1. Отвечай только на основе пунктов ПДД, которые даны ниже. Не используй знания со стороны.
2. Если в пунктах нет прямого ответа на вопрос, так и скажи. Но если в пунктах есть правила, которые помогают водителю в описанной ситуации, кратко объясни их. Не додумывай ничего, чего нет в пунктах.
3. Не определяй, кто виноват в ДТП. Перечисли обязанности каждого участника по пунктам.
4. Используй только пункты, которые прямо относятся к вопросу. Остальные не пересказывай.
5. Ответ — не больше 4–5 предложений, простым языком. В тексте ссылайся на пункты по номеру, например «(п. 81)».
6. В cited_rules перечисли номера пунктов, на которые опирается ответ, строками, ровно как они написаны после слова «Пункт»: например ["81", "58"]. Даже если прямого ответа нет, укажи пункты, которые использовал для объяснения.

Верни ответ строго в формате JSON:
{"answer": "текст ответа", "cited_rules": ["81", "58"], "found_in_rules": true}
found_in_rules = false, если прямого ответа в пунктах нет."""

class LLMAnswer(BaseModel):
    answer: str
    cited_rules: list[str]
    found_in_rules: bool

async def answer_question(question: str, context: str) -> tuple[LLMAnswer, int, int]:
    response = await openai_client.chat.completions.create(
        model=settings.chat_model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Пункты ПДД:\n\n{context}\n\nВопрос водителя: {question}"},
        ],
        reasoning_effort="low",
    )    
    content = response.choices[0].message.content or "{}"
    answer = LLMAnswer.model_validate_json(content)

    usage = response.usage
    prompt_tokens = usage.prompt_tokens if usage else 0
    completion_tokens = usage.completion_tokens if usage else 0
    return answer, prompt_tokens, completion_tokens