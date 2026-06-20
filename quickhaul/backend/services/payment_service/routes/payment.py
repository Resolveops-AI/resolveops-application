from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from services.payment_service.models.payment_model import PaymentCreate, PaymentDB
from services.payment_service.services.payment_service import payment_service

router = APIRouter()

@router.post("/create-order", response_model=PaymentDB)
async def create_order(payment_data: PaymentCreate):
    return await payment_service.create_order(payment_data)

@router.post("/pay/{payment_id}", response_model=PaymentDB)
async def process_payment(
    payment_id: str, 
    status: Optional[str] = Query(None, description="Manual success or failure trigger (SUCCESS/FAILED)")
):
    payment = await payment_service.process_payment(payment_id, status)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.get("/payment/{payment_id}", response_model=PaymentDB)
async def get_payment(payment_id: str):
    payment = await payment_service.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
