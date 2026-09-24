from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from pdd_ai_coach.db import get_session
from pdd_ai_coach.llm import answer_question, embed
from pdd_ai_coach.models import RuleChunk, RuleRow
from pdd_ai_coach.search import retrieve

app = FastAPI(title="PDD AI Coach")

SessionDep = Annotated[AsyncSession, Depends(get_session)]


class Rule(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    number: str
    text: str
    chapter_number: int
    chapter_title: str
    note: str

class SemanticHit(BaseModel):
    rule: Rule
    matched_text: str
    score: float

class AskRequest(BaseModel):
    question: str
class AskResponse(BaseModel):
    answer: str
    found_in_rules: bool
    citations: list[Rule]
    prompt_tokens: int
    completion_tokens: int    


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/rules")
async def search_rules(q: str, session: SessionDep) -> list[Rule]:
    query = func.websearch_to_tsquery("russian", q)
    stmt = (
        select(RuleRow)
        .where(RuleRow.tsv.op("@@")(query))
        .order_by(func.ts_rank(RuleRow.tsv, query).desc())
        .limit(10)
    )
    result = await session.execute(stmt)
    return [Rule.model_validate(row) for row in result.scalars()]


@app.get("/v1/rules/{number}")
async def get_rule(number: str, session: SessionDep) -> Rule:
    result = await session.execute(select(RuleRow).where(RuleRow.number == number))
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return Rule.model_validate(row)


@app.get("/v1/semantic-search")
async def semantic_search(q: str, session: SessionDep) -> list[SemanticHit]:
    query_vector = await embed(q)
    distance = RuleChunk.embedding.cosine_distance(query_vector)

    stmt = (
        select(RuleRow, RuleChunk.text, distance)
        .join(RuleChunk, RuleChunk.rule_id == RuleRow.id)
        .order_by(distance)
        .limit(20)
    )
    rows = (await session.execute(stmt)).all()

    hits: list[SemanticHit] = []
    seen: set[str] = set()
    for rule, chunk_text, dist in rows:
        if rule.number in seen:
            continue
        seen.add(rule.number)
        hits.append(
            SemanticHit(
                rule=Rule.model_validate(rule),
                matched_text=chunk_text,
                score=round(1 - dist, 3),
            )
        )
        if len(hits) == 5:
            break
    return hits

@app.post("/v1/ask")   
async def ask(body: AskRequest, session: SessionDep) -> AskResponse:
    hits = await retrieve(session, body.question)
    context = "\n\n".join(
        f"[Пункт {hit.rule.number}]\n{hit.chunk_text}" for hit in hits
    )

    llm_answer, prompt_tokens, completion_tokens = await answer_question(body.question, context)

    rules_by_number = {hit.rule.number: hit.rule for hit in hits}

    citations = [
        Rule.model_validate(rules_by_number[number])
        for number in llm_answer.cited_rules
        if number in rules_by_number
    ]

    llm_answer, prompt_tokens, completion_tokens = await answer_question(body.question, context)

    return AskResponse(
        answer=llm_answer.answer,
        found_in_rules=llm_answer.found_in_rules,
        citations=citations,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
    )
    
