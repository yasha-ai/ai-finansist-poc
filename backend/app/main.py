from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, Base, async_session
from app.models import Certificate, Raffle, CharityOption
from app.routes import certificates, purchases, raffles, charity


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed data
    async with async_session() as db:
        from sqlalchemy import select
        result = await db.execute(select(Certificate))
        if not result.scalars().first():
            db.add_all([
                Certificate(
                    title="Базовая финансовая грамотность",
                    description="Консультация с AI по основам личных финансов: бюджет, накопления, долги",
                    price=100000,  # 1000 rubles in kopeks
                    ai_prompt="Ты финансовый советник.",
                ),
                Certificate(
                    title="Инвестиции для начинающих",
                    description="AI-советник по инвестициям, пассивному доходу и портфельной стратегии",
                    price=250000,
                    ai_prompt="Ты эксперт по инвестициям.",
                ),
                Certificate(
                    title="Налоговая оптимизация",
                    description="Консультация по налогам, вычетам и легальной оптимизации для физлиц и ИП",
                    price=500000,
                    ai_prompt="Ты налоговый консультант.",
                ),
            ])

            # Seed raffle
            db.add(Raffle(
                title="Бесплатный сертификат 'Инвестиции'",
                description="Выиграйте бесплатную AI-консультацию по инвестициям!",
                certificate_id=None,  # will be set after cert creation
                ends_at=datetime.utcnow() + timedelta(days=7),
            ))

            # Seed charity options
            db.add_all([
                CharityOption(
                    title="Финансовая грамотность для детей",
                    description="Обучение школьников основам управления деньгами",
                    votes=42,
                ),
                CharityOption(
                    title="Помощь пенсионерам",
                    description="Консультации по пенсионным накоплениям и льготам",
                    votes=28,
                ),
                CharityOption(
                    title="Поддержка начинающих предпринимателей",
                    description="Менторство и финансовое планирование для стартапов",
                    votes=35,
                ),
            ])

            await db.commit()

    yield


app = FastAPI(
    title="AI Finansist",
    description="Telegram Mini App for financial literacy certificates",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(certificates.router)
app.include_router(purchases.router)
app.include_router(raffles.router)
app.include_router(charity.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# Serve frontend static files
import os
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "out")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
