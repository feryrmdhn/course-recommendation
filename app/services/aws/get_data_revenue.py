from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import date
from app.utils.utils import validate_api_key
from app.db.conn import postgreSQL_connection

router = APIRouter()

@router.get("/v1/revenue", tags=["Revenue"], description="Get revenue data from 2023 to present")
async def get_data_revenue(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    api_key: str = Depends(validate_api_key)
):
    cursor = None

    try:
        cursor = postgreSQL_connection.get_cursor()

        # Validate date range
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="Start date must be earlier than or equal to end date.")

        # Query to fetch revenue data
        cursor.execute("""
            SELECT
                date,
                ARRAY_AGG(DISTINCT course) AS courses,
                SUM(total_order) AS total_order,
                SUM(total_price) AS total_price
            FROM revenue
            WHERE date BETWEEN %s AND %s
            GROUP BY date
            ORDER BY date;
        """, (start_date, end_date))

        # Get data as list of dictionaries
        data = [
            {
                key: [course.strip() for course in value.split(",")] if key == "course" else value
                for key, value in zip([desc[0] for desc in cursor.description], row)
            }
            for row in cursor.fetchall()
        ]

        cursor.close()

        return {
            "status": 200,
            "message": "Success",
            "total": len(data),
            "total_revenue": sum(item['total_price'] for item in data),
            "data": data
        }

    except Exception as e:
        if cursor:
            cursor.execute("ROLLBACK;")
            cursor.close()
        raise HTTPException(status_code=500, detail=str(e))