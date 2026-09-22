from fastapi import FastAPI

app = FastAPI(title="PDD AI Coach")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}