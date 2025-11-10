from typing import Annotated, Optional
from pydantic import BaseModel, EmailStr, Field, StringConstraints, ConfigDict
from annotated_types import Ge, Le

NameStr = Annotated[str, StringConstraints(min_length = 1, max_length = 100)]
CustomerSinceStr = Annotated[int, Ge(2000), Le(2100)]
OrderNumberStr = Annotated[int, Ge(3), Le(20)]
TotalCentsStr = Annotated[int, Ge(1), Le(1000000)]

class CustomerCreate(BaseModel):
    id: int
    name: NameStr
    email: EmailStr
    customer_since: CustomerSinceStr

class CustomerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: NameStr
    email: EmailStr
    customer_since: CustomerSinceStr

class OrderCreate(BaseModel):
    id: int
    order_number: OrderNumberStr
    total_cents: TotalCentsStr

class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_number: OrderNumberStr
    total_cents: TotalCentsStr
    customer_id: int

class CustomerPatch(BaseModel):
    id: Optional[int] = None
    name: Optional[NameStr] = None
    email: Optional[EmailStr] = None
    customer_since: Optional[CustomerSinceStr] = None
