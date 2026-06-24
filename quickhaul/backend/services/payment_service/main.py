from fastapi import FastAPI, APIRouter
from services.payment_service.routes.payment import router as payment_router
import uvicorn
import sys
from pathlib import Path

# Add backend root to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Quick-Haul Payment Service", version="1.0.0")

router = APIRouter(prefix="/api/payments")

@router.get("")
@router.get("/")
async def root_health():
    return {"status": "healthy"}

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "payment-service"}

app.include_router(router)
app.include_router(payment_router, prefix="/api/payments", tags=["Payment"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8006, reload=True)
