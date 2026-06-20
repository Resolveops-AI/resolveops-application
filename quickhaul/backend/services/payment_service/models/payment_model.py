from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class PaymentBase(BaseModel):
    booking_id: str
    amount: float

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    status: str

class PaymentDB(PaymentBase):
    payment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "CREATED"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "payment_id": "550e8400-e29b-41d4-a716-446655440000",
                "booking_id": "BOOK123",
                "amount": 150.50,
                "status": "CREATED",
                "created_at": "2024-04-26T12:00:00"
            }
        }
