from fastapi import FastAPI
from services.payment_service.routes.payment import router as payment_router
import uvicorn
import sys
from pathlib import Path

# Add backend root to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Quick-Haul Payment Service", version="1.0.0")

app.include_router(payment_router, tags=["Payment"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "payment-service"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8006, reload=True)
