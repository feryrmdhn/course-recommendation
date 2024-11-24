from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import boto3
import json
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

# Config SageMaker
session = boto3.Session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)
sagemaker_runtime = session.client('sagemaker-runtime')
endpoint_name = os.getenv("ENDPOINT_NAME")

# Pydantic models for request/response
class CourseRequest(BaseModel):
    course_name: str
    school_id: int
    top_n: Optional[int] = 10

class CourseData(BaseModel):
    course_name: str
    categories: List[str]
    school_id: int
    similarity: float

class APIResponse(BaseModel):
    status: int
    message: str
    data: List[CourseData]

@router.post("/recommendation", response_model=APIResponse)
async def get_recommendations(request: CourseRequest):
    try:
        input_data = {
            "course_name": request.course_name,
            "school_id": request.school_id,
            "top_n": request.top_n
        }
        
        # Invoke SageMaker endpoint
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=endpoint_name, 
            ContentType='application/json',
            Body=json.dumps(input_data)
        )
        
        # Parse response
        response_body = json.loads(response['Body'].read())
        
        # Check if response is an error message
        if isinstance(response_body, str):
            raise HTTPException(status_code=400, detail=response_body)
        
        # Format response data
        formatted_data = [
            CourseData(
                course_name=course['course_name'],
                categories=course['categories'].split(',') if isinstance(course['categories'], str) else [],
                school_id=request.school_id,
                similarity=round(float(course['similarity']), 4)
            )
            for course in response_body
        ]
        
        return {
            "status": 200,
            "message": "Success",
            "data": formatted_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))