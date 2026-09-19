from sqlalchemy.orm import Session

from .models import AuditLog


def write_audit(
    db: Session,
    user,
    action: str,
    resource: str,
    detail: str = "",
):
    log = AuditLog(
        user_id=user.id if user else None,
        action=action,
        resource=resource,
        detail=detail,
    )

    db.add(log)
