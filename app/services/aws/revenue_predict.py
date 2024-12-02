from fastapi import APIRouter, HTTPException, Depends
from app.utils.utils import validate_api_key
from app.db.conn import postgreSQL_connection
from dotenv import load_dotenv
import os
import boto3
import json
from decimal import Decimal
import numpy as np
import pandas as pd

load_dotenv()
router = APIRouter()

# Config SageMaker
session = boto3.Session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)
sagemaker_runtime = session.client('sagemaker-runtime')
endpoint_name = os.getenv("ENDPOINT_NAME_REVENUE")

@router.get("/v1/revenue_predict", tags=["Revenue"], description="Predict total revenue based on average data from the last 3 months.")
async def predict_revenue(api_key: str = Depends(validate_api_key)):
    
    cursor = None

    def predict_model(input_data):
        # Input
        rounded_total_order = int(input_data["total_order"])
        rounded_price = int(input_data["price"])

        data = [rounded_total_order, rounded_price]

        X = np.array([data])

        # convert to scv format
        data_converted = '\n'.join([','.join(map(str, row)) for row in X])

        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            Body=data_converted,
            ContentType="text/csv",
            Accept='text/csv'
        )
        result = response['Body'].read().decode('utf-8')
        
        return round(float(result.strip()), 5)

    try:
        cursor = postgreSQL_connection.get_cursor()

        cursor.execute("""
                SELECT 
                    AVG(total_order) AS avg_total_order, 
                    AVG(price) AS avg_price
                FROM revenue
                WHERE date >= (CURRENT_DATE - INTERVAL '3 months')
            """)
        avg_data = cursor.fetchone()

        if not avg_data or not avg_data[0] or not avg_data[1]:
            raise HTTPException(status_code=404, detail="No sufficient data found for prediction.")

        # Convert Decimal to float
        avg_total_order = float(avg_data[0]) if isinstance(avg_data[0], Decimal) else avg_data[0]
        avg_price = float(avg_data[1]) if isinstance(avg_data[1], Decimal) else avg_data[1]

        # Prepare input for model
        input_data = {"total_order": avg_total_order, "price": avg_price}

        predicted_revenue = predict_model(input_data)
        cursor.close()

        return {
            "status": 200,
            "message": "Success",
            "data": {
                "predicted_revenue": predicted_revenue
            }
        }

    except Exception as e:
        if cursor:
            cursor.execute("ROLLBACK;")
            cursor.close()
        raise HTTPException(status_code=500, detail=str(e))