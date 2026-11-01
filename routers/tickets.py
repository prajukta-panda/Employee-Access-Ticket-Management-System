
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from authentication import get_db, get_current_user
from models import User, Ticket
from schemas import TicketCreate, TicketResponse , TicketUpdate
from enums import TicketStatus,UserRole
from schemas import TicketStatusUpdate


router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)


@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED
)
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        priority=ticket_data.priority,
        status=TicketStatus.OPEN,
        created_by=current_user.id,
        assigned_to=None
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    return new_ticket
@router.get("/")
def list_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tickets = (
        db.query(Ticket)
        .filter(Ticket.created_by == current_user.id)
        .order_by(Ticket.created_at.desc())
        .all()
    )

    return tickets

@router.get("/{ticket_id}")
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    # Check whether the ticket exists
    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # Admins and managers can view all tickets
    if current_user.role in (UserRole.ADMIN, UserRole.MANAGER):
        return ticket

    # Employees can view only tickets they created
    if current_user.role == UserRole.EMPLOYEE:
        if ticket.created_by == current_user.id:
            return ticket

    # Support users can view only tickets assigned to them
    if current_user.role == UserRole.SUPPORT:
        if ticket.assigned_to == current_user.id:
            return ticket

    raise HTTPException(
        status_code=403,
        detail="You do not have permission to view this ticket"
    )
@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Find the ticket
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # 2. Check permission
    if current_user.role == UserRole.ADMIN:
        pass

    elif current_user.role == UserRole.MANAGER:
        pass

    elif current_user.role == UserRole.EMPLOYEE:
        if ticket.created_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can update only tickets you created"
            )

    elif current_user.role == UserRole.SUPPORT:
        if ticket.assigned_to != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can update only tickets assigned to you"
            )

    # 3. Get only the fields sent in the request
    update_data = ticket_data.model_dump(exclude_unset=True) #This is the key line for partial updates. It returns only the fields the client actually sent, rather than every field in the schema.

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one field to update"
        )

    # 4. Update the ticket fields
    for field, value in update_data.items():
        if value is None:
            raise HTTPException(
                status_code=422,
                detail=f"{field} cannot be null"
            )

        setattr(ticket, field, value)#This dynamically updates the relevant model attribute. If field is "priority", it behaves like:ticket.priority = value

    # 5. Update the timestamp
    ticket.updated_at = datetime.utcnow()

    # 6. Save changes to the database
    db.commit()
    db.refresh(ticket)

    return ticket

@router.patch("/{ticket_id}/assign", response_model=TicketResponse)
def assign_ticket(
    ticket_id: int,
    assignee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Only admins and managers can assign tickets
    if current_user.role not in (UserRole.ADMIN, UserRole.MANAGER):
        raise HTTPException(
            status_code=403,
            detail="Only admins and managers can assign tickets"
        )

    # 2. Find the ticket
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # 3. Find the intended assignee
    assignee = (
        db.query(User)
        .filter(User.id == assignee_id)
        .first()
    )

    if assignee is None:
        raise HTTPException(
            status_code=404,
            detail="Assignee not found"
        )

    # 4. Ensure the assignee is an active support engineer
    if assignee.role != UserRole.SUPPORT:
        raise HTTPException(
            status_code=400,
            detail="Tickets can only be assigned to support engineers"
        )

    if not assignee.is_active:
        raise HTTPException(
            status_code=400,
            detail="Cannot assign a ticket to an inactive user"
        )

    # 5. Assign and save
    ticket.assigned_to = assignee.id
    ticket.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(ticket)

    return ticket 
@router.patch("/{ticket_id}/status")
def update_ticket_status(
    ticket_id: int,
    status_data: TicketStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find the ticket
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    new_status = status_data.status

    # Admin and Manager permissions
    if current_user.role in (UserRole.ADMIN, UserRole.MANAGER):
        pass

    # Support Engineer permissions
    elif current_user.role == UserRole.SUPPORT:
        if ticket.assigned_to != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only update tickets assigned to you"
            )

        if ticket.status == TicketStatus.OPEN and new_status == TicketStatus.IN_PROGRESS:
            pass

        elif ticket.status == TicketStatus.IN_PROGRESS and new_status == TicketStatus.RESOLVED:
            pass

        else:
            raise HTTPException(
                status_code=400,
                detail="Support engineers can only move tickets from OPEN to IN_PROGRESS or IN_PROGRESS to RESOLVED"
            )

    # Employee permissions
    elif current_user.role == UserRole.EMPLOYEE:
        if ticket.created_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only close tickets created by you"
            )

        if ticket.status != TicketStatus.RESOLVED or new_status != TicketStatus.CLOSED:
            raise HTTPException(
                status_code=400,
                detail="You can only close a resolved ticket"
            )

    else:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to update ticket status"
        )

    # Update the status
    ticket.status = new_status
    ticket.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(ticket)

    return {
        "message": "Ticket status updated successfully",
        "ticket_id": ticket.id,
        "status": ticket.status
    }      