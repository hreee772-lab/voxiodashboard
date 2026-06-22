from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

# Requests
class SignupRequest(BaseModel):
    company_name: str
    company_email: EmailStr
    password: str
    domain: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Responses
class ClientResponse(BaseModel):
    id: UUID
    company_name: str
    company_email: EmailStr
    domain: Optional[str] = None
    plan: str
    is_active: bool
    created_at: datetime
    team_size: Optional[str] = None
    industry: Optional[str] = None

class UserResponse(BaseModel):
    id: UUID
    client_id: UUID
    email: EmailStr
    full_name: str
    role: str
    department: Optional[str] = None
    is_active: bool
    created_at: datetime
    onboarding_completed: Optional[bool] = False
    display_preference: Optional[str] = "full_name"

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    client: ClientResponse
