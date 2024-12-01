from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import boto3
import json
from typing import List, Optional
import os
from app.utils.utils import validate_api_key
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
    total: int
    data: List[CourseData]

@router.post("/v1/recommendation", response_model=APIResponse)
async def course_recommendations(request: CourseRequest, api_key: str = Depends(validate_api_key)):
    cursor = None

    try:
        input_data = {
            "text": request.course_name,
            "school_id": request.school_id,
            "top_n": request.top_n
        }

        json_input_data = json.dumps(input_data)

        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=endpoint_name, 
            ContentType='application/json',
            Accept='application/json',
            Body=json_input_data
        )
        
        # Read and parse the response
        response_body = response['Body'].read().decode('utf-8')
        
        if not response_body:
            raise HTTPException(status_code=500, detail="Empty response from model.")
        
        try:
            response_json = json.loads(response_body)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Failed to decode response body.")
        
        # Handle potential error response
        if isinstance(response_json, dict) and 'error' in response_json:
            raise HTTPException(status_code=400, detail=response_json['error'])
        
        formatted_data = [
            CourseData(
                course_name=course['name'],
                categories=[category.strip() for category in course['categories'].split(',')] if isinstance(course['categories'], str) else [],
                school_id=request.school_id,
                similarity=round(float(course['similarity']), 2)
            )
            for course in response_json
        ]
        
        return {
            "status": 200,
            "message": "Success",
            "total": len(formatted_data),
            "data": formatted_data
        }
    
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
