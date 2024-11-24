from fastapi import FastAPI
from app.services.aws import recommendation

app = FastAPI()

app.include_router(recommendation.router)
