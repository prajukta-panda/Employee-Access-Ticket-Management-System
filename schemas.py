from pydantic import BaseModel, EmailStr
from enums import UserRole, Priority,TicketStatus
from datetime import datetime
from typing import Optional


#pydantic schema used as a format what user should give in swagger ui just like html in frontend
# -------------------------
# USER SCHEMAS
# -------------------------

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool

    model_config = {
        "from_attributes": True
    }


# -------------------------
# TICKET SCHEMAS
# -------------------------

class TicketCreate(BaseModel):
    title: str
    description: str
    priority: Priority


# -------------------------
# COMMENT SCHEMAS
# -------------------------

class CommentCreate(BaseModel):
    message: str


# -------------------------
# AUTH SCHEMAS
# -------------------------

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None

#login requets schema

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: Priority
    status: TicketStatus
    created_by: int
    #created_by_name: str
    assigned_to: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }    
class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: Priority | None = None    

#Why do we use None = None? This is called a partial update.

#When updating a ticket, the user may want to change just one field.  


class AdminUserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole
class TicketStatusUpdate(BaseModel):
    status: TicketStatus
class CommentResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}   