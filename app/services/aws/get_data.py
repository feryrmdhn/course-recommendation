from fastapi import APIRouter, HTTPException, Depends
from app.utils.utils import validate_api_key
from app.db.conn import postgreSQL_connection

router = APIRouter()

@router.get("/v1/courses")
async def get_data_courses(api_key: str = Depends(validate_api_key)):
    cursor = None

    try:
        cursor = postgreSQL_connection.get_cursor()

        # query postgreSQL to execute courses table
        cursor.execute("SELECT id, name, categories, school_id, total_enrollment FROM courses ORDER BY RANDOM() LIMIT 50;")

        # get data as list of dictionaries
        data = [
            {
                key: [category.strip() for category in value.split(",")] if key == "categories" else value
                for key, value in zip([desc[0] for desc in cursor.description], row)
            }    
            for row in cursor.fetchall()
        ]

        cursor.close()

        return {
            "status": 200,
            "message": "Success",
            "total": len(data),
            "data": data
        }

    except Exception as e:
        if cursor:
            cursor.execute("ROLLBACK;")
            cursor.close()
        raise HTTPException(status_code=500, detail=str(e))