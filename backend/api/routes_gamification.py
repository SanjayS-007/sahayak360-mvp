"""
Gamification routes — XP, levels, streaks, badges, leaderboard.
"""

from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, require_role
from db.models import StudentGamification, User, Notification
from db.postgres import get_db

router = APIRouter()

# XP thresholds for levels
LEVEL_THRESHOLDS = [0, 100, 300, 600, 1000, 1500, 2200, 3000, 4000, 5200, 6500]

# Badge definitions
BADGE_DEFS = {
    "first_practice": {"name": "First Steps", "desc": "Complete your first practice", "icon": "🎯"},
    "streak_3": {"name": "On a Roll", "desc": "3-day practice streak", "icon": "🔥"},
    "streak_7": {"name": "Week Warrior", "desc": "7-day practice streak", "icon": "⚡"},
    "streak_30": {"name": "Unstoppable", "desc": "30-day practice streak", "icon": "💎"},
    "perfect_score": {"name": "Perfectionist", "desc": "Score 100% on any practice", "icon": "✨"},
    "ten_practices": {"name": "Dedicated", "desc": "Complete 10 practices", "icon": "📚"},
    "fifty_practices": {"name": "Scholar", "desc": "Complete 50 practices", "icon": "🎓"},
    "level_5": {"name": "Rising Star", "desc": "Reach level 5", "icon": "⭐"},
    "level_10": {"name": "Master Mind", "desc": "Reach level 10", "icon": "🏆"},
    "hundred_correct": {"name": "Century", "desc": "100 correct answers", "icon": "💯"},
}


def _compute_level(xp: int) -> int:
    """Compute level from XP."""
    for i in range(len(LEVEL_THRESHOLDS) - 1, -1, -1):
        if xp >= LEVEL_THRESHOLDS[i]:
            return i + 1
    return 1


def _xp_for_next_level(level: int) -> int:
    """XP needed for next level."""
    if level < len(LEVEL_THRESHOLDS):
        return LEVEL_THRESHOLDS[level]
    return LEVEL_THRESHOLDS[-1] + (level - len(LEVEL_THRESHOLDS)) * 1500


@router.get("/profile")
async def get_gamification_profile(
    user: User = Depends(require_role("student")),
    db: AsyncSession = Depends(get_db),
):
    """Get student's gamification profile."""
    result = await db.execute(
        select(StudentGamification).where(StudentGamification.student_id == user.user_id)
    )
    gam = result.scalar_one_or_none()

    if not gam:
        # Create default profile
        gam = StudentGamification(student_id=user.user_id, xp=0, level=1, badges=[])
        db.add(gam)
        await db.commit()
        await db.refresh(gam)

    next_level_xp = _xp_for_next_level(gam.level)
    current_level_xp = LEVEL_THRESHOLDS[gam.level - 1] if gam.level <= len(LEVEL_THRESHOLDS) else 0
    progress = ((gam.xp - current_level_xp) / max(1, next_level_xp - current_level_xp)) * 100

    return {
        "xp": gam.xp,
        "level": gam.level,
        "streak_days": gam.streak_days,
        "longest_streak": gam.longest_streak,
        "badges": gam.badges or [],
        "total_practices": gam.total_practices,
        "total_correct": gam.total_correct,
        "total_questions": gam.total_questions,
        "accuracy": round(gam.total_correct / max(1, gam.total_questions) * 100, 1),
        "next_level_xp": next_level_xp,
        "level_progress": round(min(100, progress), 1),
        "all_badges": [
            {**v, "id": k, "earned": any(b.get("id") == k for b in (gam.badges or []))}
            for k, v in BADGE_DEFS.items()
        ],
    }


@router.get("/leaderboard")
async def get_leaderboard(
    user: User = Depends(require_role("student")),
    db: AsyncSession = Depends(get_db),
):
    """Get class leaderboard."""
    # Get student's class
    class_section = user.class_section or "9-A"

    # Get all students in same class with gamification
    result = await db.execute(
        select(StudentGamification, User.full_name, User.user_id)
        .join(User, User.user_id == StudentGamification.student_id)
        .where(User.class_section == class_section)
        .order_by(desc(StudentGamification.xp))
    )
    rows = result.all()

    leaderboard = []
    my_rank = 0
    for i, (gam, name, uid) in enumerate(rows, 1):
        leaderboard.append({
            "rank": i,
            "name": name,
            "user_id": uid,
            "xp": gam.xp,
            "level": gam.level,
            "streak": gam.streak_days,
            "is_me": uid == user.user_id,
        })
        if uid == user.user_id:
            my_rank = i

    # If student not in leaderboard yet, add them
    if my_rank == 0:
        leaderboard.append({
            "rank": len(leaderboard) + 1,
            "name": user.full_name,
            "user_id": user.user_id,
            "xp": 0,
            "level": 1,
            "streak": 0,
            "is_me": True,
        })
        my_rank = len(leaderboard)

    return {
        "leaderboard": leaderboard[:20],
        "my_rank": my_rank,
        "total_students": len(leaderboard),
    }


async def award_xp(db: AsyncSession, student_id: str, xp_amount: int, correct: int, total: int, score: float):
    """Award XP and check badges. Called from practice submit."""
    result = await db.execute(
        select(StudentGamification).where(StudentGamification.student_id == student_id)
    )
    gam = result.scalar_one_or_none()

    today = date.today()
    new_badges = []

    if not gam:
        gam = StudentGamification(
            student_id=student_id,
            xp=0, level=1, streak_days=0, longest_streak=0,
            badges=[], total_practices=0, total_correct=0, total_questions=0,
        )
        db.add(gam)

    # Update stats
    gam.xp += xp_amount
    gam.total_practices += 1
    gam.total_correct += correct
    gam.total_questions += total
    gam.level = _compute_level(gam.xp)

    # Update streak
    if gam.last_practice_date:
        days_diff = (today - gam.last_practice_date).days
        if days_diff == 1:
            gam.streak_days += 1
        elif days_diff > 1:
            gam.streak_days = 1
        # same day: no change to streak
    else:
        gam.streak_days = 1

    gam.last_practice_date = today
    if gam.streak_days > (gam.longest_streak or 0):
        gam.longest_streak = gam.streak_days

    # Check badges
    existing_ids = {b.get("id") for b in (gam.badges or [])}
    badges_list = list(gam.badges or [])

    def _award(badge_id):
        if badge_id not in existing_ids:
            badges_list.append({"id": badge_id, "name": BADGE_DEFS[badge_id]["name"], "earned_at": today.isoformat()})
            new_badges.append(BADGE_DEFS[badge_id])

    if gam.total_practices == 1:
        _award("first_practice")
    if gam.total_practices >= 10:
        _award("ten_practices")
    if gam.total_practices >= 50:
        _award("fifty_practices")
    if score >= 1.0:
        _award("perfect_score")
    if gam.streak_days >= 3:
        _award("streak_3")
    if gam.streak_days >= 7:
        _award("streak_7")
    if gam.streak_days >= 30:
        _award("streak_30")
    if gam.level >= 5:
        _award("level_5")
    if gam.level >= 10:
        _award("level_10")
    if gam.total_correct >= 100:
        _award("hundred_correct")

    gam.badges = badges_list
    gam.updated_at = datetime.utcnow()

    # Create badge notifications
    for badge in new_badges:
        notif = Notification(
            user_id=student_id,
            type="badge",
            title=f"Badge Earned: {badge['name']} {badge['icon']}",
            message=badge["desc"],
            data={"badge": badge["name"]},
        )
        db.add(notif)

    return new_badges
