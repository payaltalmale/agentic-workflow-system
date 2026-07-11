"""
Entrypoint: wires up the FastAPI app and initializes the SQLite schema
on startup. Run with: uvicorn main:app --reload --port 8000
"""
from fastapi import FastAPI
from api.routes import router
from memory.sqlite_memory import init_db

app = FastAPI(title="Agentic Workflow System")


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(router)


@app.get("/")
def health():
    return {"status": "ok", "service": "agentic-workflow"}
