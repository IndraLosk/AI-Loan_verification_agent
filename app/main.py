from fastapi import FastAPI
from app.routers import checks
from app.database import engine
from app.models import Base

app = FastAPI(title="Check Documents API", version="1.0")

# Создание таблиц в БД (если не используются миграции)
Base.metadata.create_all(bind=engine)

# Подключаем роутеры
app.include_router(checks.router)

@app.get("/")
def root():
    return {"message": "Сервис проверки документов работает"}