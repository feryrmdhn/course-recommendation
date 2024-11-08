from fastapi import HTTPException, Depends
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")

if API_KEY is None:
    raise ValueError("API_KEY environment variable is not set")

API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME)

def validate_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
