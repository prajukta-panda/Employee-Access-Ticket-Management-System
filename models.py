from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Enum
)
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from enums import UserRole, Priority, TicketStatus
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tickets_created = relationship(
        "Ticket",
        foreign_keys="Ticket.created_by",
        back_populates="creator"
    )

    tickets_assigned = relationship(
        "Ticket",
        foreign_keys="Ticket.assigned_to",
        back_populates="assignee"
    )

    comments = relationship("Comment", back_populates="user")

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    priority = Column(Enum(Priority), nullable=False)
    status = Column(Enum(TicketStatus), nullable=False)

    created_by = Column(Integer, ForeignKey("users.id"))
    assigned_to = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="tickets_created"
    )

    assignee = relationship(
        "User",
        foreign_keys=[assigned_to],
        back_populates="tickets_assigned"
    )

    comments = relationship("Comment", back_populates="ticket")
class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)

    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="comments")
    user = relationship("User", back_populates="comments")
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)

    action = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"))
    ticket_id = Column(Integer, ForeignKey("tickets.id"))

    timestamp = Column(DateTime, default=datetime.utcnow)            