import random
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Raffle, RaffleEntry, RaffleStatus, User
from app.auth import get_current_user

router = APIRouter(prefix="/api/raffles", tags=["raffles"])


@router.get("")
async def list_raffles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Raffle).where(Raffle.status == RaffleStatus.ACTIVE).order_by(Raffle.ends_at)
    )
    raffles = result.scalars().all()

    items = []
    for r in raffles:
        count_result = await db.execute(
            select(func.count()).select_from(RaffleEntry).where(RaffleEntry.raffle_id == r.id)
        )
        count = count_result.scalar()
        items.append({
            "id": str(r.id),
            "title": r.title,
            "description": r.description,
            "entries_count": count,
            "max_entries": r.max_entries,
            "ends_at": r.ends_at.isoformat(),
        })

    return {"raffles": items}


@router.post("/{raffle_id}/join")
async def join_raffle(
    raffle_id: UUID,
    user_data: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get raffle
    result = await db.execute(select(Raffle).where(Raffle.id == raffle_id))
    raffle = result.scalar_one_or_none()
    if not raffle or raffle.status != RaffleStatus.ACTIVE:
        raise HTTPException(status_code=404, detail="Raffle not found or inactive")

    if raffle.ends_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Raffle has ended")

    # Get or create user
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

    # Check if already entered
    result = await db.execute(
        select(RaffleEntry).where(
            RaffleEntry.raffle_id == raffle_id,
            RaffleEntry.user_id == user.id,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already entered")

    entry = RaffleEntry(raffle_id=raffle_id, user_id=user.id)
    db.add(entry)
    await db.commit()

    return {"message": "Вы участвуете в розыгрыше!", "raffle_id": str(raffle_id)}


@router.post("/{raffle_id}/draw")
async def draw_winner(raffle_id: UUID, db: AsyncSession = Depends(get_db)):
    """Draw a random winner (admin endpoint)."""
    result = await db.execute(select(Raffle).where(Raffle.id == raffle_id))
    raffle = result.scalar_one_or_none()
    if not raffle:
        raise HTTPException(status_code=404, detail="Raffle not found")

    result = await db.execute(
        select(RaffleEntry).where(RaffleEntry.raffle_id == raffle_id)
    )
    entries = result.scalars().all()
    if not entries:
        raise HTTPException(status_code=400, detail="No entries")

    winner_entry = random.choice(entries)
    raffle.winner_id = winner_entry.user_id
    raffle.status = RaffleStatus.COMPLETED
    await db.commit()

    result = await db.execute(select(User).where(User.id == winner_entry.user_id))
    winner = result.scalar_one()

    return {
        "winner": {
            "username": winner.username,
            "first_name": winner.first_name,
            "telegram_id": winner.telegram_id,
        },
        "raffle_title": raffle.title,
    }
