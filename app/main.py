from fastapi import FastAPI
from app.services.aws import recommendation
from app.services.aws import get_data

app = FastAPI()

app.include_router(get_data.router)

app.include_router(recommendation.router)
