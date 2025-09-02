from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from datetime import datetime

class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class PaymentMethod(Enum):
    USDT = "usdt"
    TRX = "trx"

@dataclass
class Product:
    id: str
    name: str
    description: str
    price: Decimal
    image_url: Optional[str] = None
    stock: int = 0

@dataclass
class Order:
    id: str
    user_id: str
    products: List[Product]
    total_amount: Decimal
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    created_at: datetime = datetime.now()
    completed_at: Optional[datetime] = None
    transaction_hash: Optional[str] = None

    @property
    def is_completed(self) -> bool:
        return self.payment_status == PaymentStatus.COMPLETED