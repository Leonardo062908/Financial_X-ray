from fastapi import FastAPI
from app.webhook import router as webhook_router

app = FastAPI(title="Financial X-Ray - WhatsApp MVP")

app.include_router(webhook_router)