from datetime import datetime

from pydantic import BaseModel, EmailStr, Field
from app.security.passwords import MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH

class UserRead(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str = Field(
        min_length=MIN_PASSWORD_LENGTH,
        max_length=MAX_PASSWORD_LENGTH,
    )
    role: str = "SECURITY"
