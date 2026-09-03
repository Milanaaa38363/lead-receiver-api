@"
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional
from app.utils import normalize_phone, InvalidPhoneError

class CreateLeadRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Имя лида")
    phone: str = Field(..., description="Телефон в любом формате")
    source: str = Field(..., min_length=1, description="Источник заявки")

    @field_validator("phone")
    def validate_phone(cls, v):
        try:
            normalize_phone(v)
            return v
        except InvalidPhoneError as e:
            raise ValueError(str(e))

class LeadHistoryResponse(BaseModel):
    id: str
    source: str
    raw_phone: str
    created_at: datetime

    class Config:
        from_attributes = True

class ClientResponse(BaseModel):
    id: str
    name: str
    phone_normalized: str

    class Config:
        from_attributes = True

class DealResponse(BaseModel):
    id: str
    client_id: str
    client: Optional[ClientResponse] = None
    status: str
    created_at: datetime
    history: List[LeadHistoryResponse] = []

    class Config:
        from_attributes = True

class CreateLeadResponse(BaseModel):
    is_new_client: bool
    client_id: str
    deal_id: str
    message: str
"@ | Out-File -Encoding utf8 app/schemas.py