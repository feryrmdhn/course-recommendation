from fastapi import FastAPI
from app.services.aws import recommendation
from app.services.aws import get_data
from app.services.aws import get_data_revenue
from app.services.aws import revenue_predict

app = FastAPI(
    title = "ML API for Dummy Eduqat"
)

app.include_router(get_data.router)

app.include_router(recommendation.router)

app.include_router(get_data_revenue.router)

app.include_router(revenue_predict.router)
