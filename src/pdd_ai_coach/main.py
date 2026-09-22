from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="PDD AI Coach")


class Rule(BaseModel):
    number: str
    title: str
    text: str


RULES: dict[str, Rule] = {
    "10.2": Rule(number="10.2", title="...", text="..."),
    "10.3": Rule(number="10.3", title="...", text="..."),
    "10.4": Rule(number="10.4", title="...", text="..."),
}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/rules/{number}")
def get_rule(number: str) -> Rule:
    rule = RULES.get(number)
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule
