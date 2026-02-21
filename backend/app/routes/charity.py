from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import CharityOption, CharityVote, User
from app.auth import get_current_user

router = APIRouter(prefix="/api/charity", tags=["charity"])


@router.get("")
async def list_options(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CharityOption).where(CharityOption.is_active == True).order_by(CharityOption.votes.desc())
    )
    options = result.scalars().all()
    total_votes = sum(o.votes for o in options)

    return {
        "options": [
            {
                "id": str(o.id),
                "title": o.title,
                "description": o.description,
                "image_url": o.image_url,
                "votes": o.votes,
                "percentage": round(o.votes / total_votes * 100, 1) if total_votes > 0 else 0,
            }
            for o in options
        ],
        "total_votes": total_votes,
    }


@router.post("/{option_id}/vote")
async def vote(
    option_id: UUID,
    user_data: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get user
    result = await db.execute(select(User).where(User.telegram_id == user_data["id"]))
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            telegram_id=user_data["id"],
            username=user_data.get("username"),
            first_name=user_data.get("first_name"),
        )
        db.add(user)
        await db.flush()

    # Check already voted
    result = await db.execute(
        select(CharityVote).where(CharityVote.user_id == user.id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Вы уже голосовали")

    # Get option
    result = await db.execute(select(CharityOption).where(CharityOption.id == option_id))
    option = result.scalar_one_or_none()
    if not option:
        raise HTTPException(status_code=404, detail="Option not found")

    vote = CharityVote(user_id=user.id, option_id=option_id)
    option.votes += 1
    db.add(vote)
    await db.commit()

    return {"message": f"Голос за '{option.title}' принят!", "votes": option.votes}
