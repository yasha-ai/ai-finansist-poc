import io
import base64
from uuid import UUID
from datetime import datetime

import qrcode
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Purchase, PurchaseStatus, Certificate, User
from app.auth import get_current_user

router = APIRouter(prefix="/api/purchases", tags=["purchases"])


class PurchaseCreate(BaseModel):
    certificate_id: str


def generate_qr_code(data: str) -> str:
    """Generate QR code as base64 string."""
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


@router.post("")
async def create_purchase(
    body: PurchaseCreate,
    user_data: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get or create user
    result = await db.execute(
        select(User).where(User.telegram_id == user_data["id"])
    )
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            telegram_id=user_data["id"],
            username=user_data.get("username"),
            first_name=user_data.get("first_name"),
        )
        db.add(user)
        await db.flush()

    # Get certificate
    result = await db.execute(
        select(Certificate).where(Certificate.id == UUID(body.certificate_id))
    )
    cert = result.scalar_one_or_none()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")

    # Create purchase (mock payment - auto-confirm)
    purchase = Purchase(
        user_id=user.id,
        certificate_id=cert.id,
        amount=cert.price,
        status=PurchaseStatus.PAID,
        payment_id=f"mock_{datetime.utcnow().timestamp()}",
        paid_at=datetime.utcnow(),
    )
    
    # Generate QR code
    qr_data = f"cert:{purchase.id}|user:{user.telegram_id}|title:{cert.title}"
    purchase.qr_code = generate_qr_code(qr_data)
    
    db.add(purchase)
    await db.commit()

    return {
        "id": str(purchase.id),
        "certificate_title": cert.title,
        "amount": cert.price,
        "status": purchase.status.value,
        "qr_code": purchase.qr_code,
        "message": "Сертификат успешно приобретён! (демо-режим)",
    }


@router.get("/my")
async def my_purchases(
    user_data: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.telegram_id == user_data["id"])
    )
    user = result.scalar_one_or_none()
    if not user:
        return {"purchases": []}

    result = await db.execute(
        select(Purchase, Certificate)
        .join(Certificate)
        .where(Purchase.user_id == user.id)
        .order_by(Purchase.created_at.desc())
    )
    rows = result.all()

    return {
        "purchases": [
            {
                "id": str(p.id),
                "certificate_title": c.title,
                "amount": p.amount,
                "status": p.status.value,
                "qr_code": p.qr_code,
                "purchased_at": p.paid_at.isoformat() if p.paid_at else None,
            }
            for p, c in rows
        ]
    }
