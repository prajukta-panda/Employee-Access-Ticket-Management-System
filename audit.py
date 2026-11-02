from models import AuditLog

def create_audit_log(
    db,
    action: str,
    user_id: int,
    ticket_id: int
):
    audit_entry = AuditLog(
        action=action,
        user_id=user_id,
        ticket_id=ticket_id
    )

    db.add(audit_entry)