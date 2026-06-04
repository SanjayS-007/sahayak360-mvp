"""
Notification routes — CRUD for in-app notifications.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from db.models import Notification, User
from db.postgres import get_db

router = APIRouter()


@router.get("/")
async def get_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(20, le=50),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get notifications for current user."""
    q = select(Notification).where(Notification.user_id == user.user_id)
    if unread_only:
        q = q.where(Notification.read == False)
    q = q.order_by(Notification.created_at.desc()).limit(limit)

    result = await db.execute(q)
    notifs = result.scalars().all()

    # Also get unread count
    count_q = select(func.count()).select_from(Notification).where(
        Notification.user_id == user.user_id,
        Notification.read == False,
    )
    unread_count = (await db.execute(count_q)).scalar() or 0

    return {
        "notifications": [
            {
                "id": str(n.id),
                "type": n.type,
                "title": n.title,
                "message": n.message,
                "data": n.data,
                "read": n.read,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in notifs
        ],
        "unread_count": unread_count,
    }


@router.post("/{notification_id}/read")
async def mark_read(
    notification_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    await db.execute(
        update(Notification)
        .where(Notification.id == notification_id, Notification.user_id == user.user_id)
        .values(read=True, read_at=datetime.utcnow())
    )
    await db.commit()
    return {"status": "ok"}


@router.post("/read-all")
async def mark_all_read(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all notifications as read."""
    await db.execute(
        update(Notification)
        .where(Notification.user_id == user.user_id, Notification.read == False)
        .values(read=True, read_at=datetime.utcnow())
    )
    await db.commit()
    return {"status": "ok"}
