from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Certificate

router = APIRouter(prefix="/api/certificates", tags=["certificates"])


@router.get("")
async def list_certificates(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Certificate).where(Certificate.is_active == True).order_by(Certificate.price)
    )
    certs = result.scalars().all()
    return {
        "certificates": [
            {
                "id": str(c.id),
                "title": c.title,
                "description": c.description,
                "price": c.price,
                "image_url": c.image_url,
            }
            for c in certs
        ]
    }


@router.get("/{cert_id}")
async def get_certificate(cert_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Certificate).where(Certificate.id == cert_id))
    cert = result.scalar_one_or_none()
    if not cert:
        return {"error": "Not found"}, 404
    return {
        "id": str(cert.id),
        "title": cert.title,
        "description": cert.description,
        "price": cert.price,
        "image_url": cert.image_url,
    }
