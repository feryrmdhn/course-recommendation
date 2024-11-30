import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DB_PUBLIC_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASS = os.getenv("DB_MASTER_PASSWORD")

class PostgreSQLConnection:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.connection = psycopg2.connect(
                host=DB_PUBLIC_HOST,
                port=DB_PORT,
                database="db_courses",
                user=DB_USERNAME,
                password=DB_PASS,
                sslmode="require"
            )
        return cls.__instance

    def get_cursor(self):
        return self.connection.cursor()

    def close_connection(self):
        self.connection.close()

postgreSQL_connection = PostgreSQLConnection()