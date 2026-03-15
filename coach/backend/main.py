import subprocess
from contextlib import asynccontextmanager

from fastapi import FastAPI


def run_migrations():
    subprocess.run(["alembic", "upgrade", "head"], check=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok", "service": "coach"}
