import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.database import connect_to_db, close_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from .api import router

@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Booking Service starting up...")
    await connect_to_db()
    yield
    logger.info("Booking Service shutting down...")
    await close_db()

app = FastAPI(
    title="Booking Service",
    description="Booking and pricing microservice",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "booking"}

if __name__ == "__main__":
    uvicorn.run("services.booking_service.main:app", host="127.0.0.1", port=8002, reload=True)
