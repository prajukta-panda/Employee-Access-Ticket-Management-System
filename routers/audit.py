from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from authentication import get_db, require_role
from models import AuditLog, User
from enums import UserRole

router = APIRouter(
    prefix="/audit",
    tags=["Audit Logs"]
)


@router.get("/")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMIN, UserRole.MANAGER)
    )
):
    logs = db.query(AuditLog).order_by(
        AuditLog.timestamp.desc()
    ).all()

    return logs