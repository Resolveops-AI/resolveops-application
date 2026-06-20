import os
import asyncio
import random
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from services.payment_service.models.payment_model import PaymentDB, PaymentCreate
from typing import Optional
from shared.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGO_URI = settings.mongo_uri
MONGO_DB_NAME = settings.mongo_db_name

class PaymentService:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URI)
        self.db = self.client[MONGO_DB_NAME]
        self.collection = self.db["payments"]

    async def create_order(self, payment_data: PaymentCreate) -> PaymentDB:
        payment = PaymentDB(**payment_data.model_dump())
        await self.collection.insert_one(payment.model_dump())
        logger.info(f"Payment order created: {payment.payment_id} for booking: {payment.booking_id}")
        return payment

    async def get_payment(self, payment_id: str) -> Optional[PaymentDB]:
        payment_dict = await self.collection.find_one({"payment_id": payment_id})
        if payment_dict:
            return PaymentDB(**payment_dict)
        return None

    async def process_payment(self, payment_id: str, manual_status: Optional[str] = None) -> Optional[PaymentDB]:
        payment = await self.get_payment(payment_id)
        
        if not payment:
            logger.warning(f"Payment {payment_id} not found")
            return None

        # Idempotency check
        if payment.status in ["SUCCESS", "FAILED"]:
            logger.info(f"Payment {payment_id} already processed with status: {payment.status}")
            return payment

        # Update to PENDING
        await self.collection.update_one(
            {"payment_id": payment_id},
            {"$set": {"status": "PENDING"}}
        )
        logger.info(f"Payment {payment_id} set to PENDING")

        # Simulate delay
        delay = random.uniform(2, 3)
        await asyncio.sleep(delay)

        # Determine final status
        if manual_status:
            final_status = manual_status.upper()
        else:
            final_status = "SUCCESS" if random.random() > 0.2 else "FAILED"

        await self.collection.update_one(
            {"payment_id": payment_id},
            {"$set": {"status": final_status}}
        )
        
        payment.status = final_status
        logger.info(f"Payment {payment_id} processed. Result: {final_status}")
        
        return payment

payment_service = PaymentService()
