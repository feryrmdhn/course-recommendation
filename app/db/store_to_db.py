import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

db_config = {
        'host': os.getenv("DB_HOST"),
        'user': os.getenv("DB_USERNAME"),
        'password': os.getenv("DB_MASTER_PASSWORD"),
        'port': os.getenv("DB_PORT"),
        'dbname': 'db_courses' # adjust with the other case
    }

connection_string = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"

# Store Data default to DB
df = pd.read_csv('./app/assets/data_courses.csv')

# Connect to PostgreSQL
engine = create_engine(connection_string)

# Save data to PostgreSQL
df.to_sql('courses', engine, if_exists='replace', index=False)

# Run python store_to_db.py in active venv terminal
# ========================================= #
print("Successed store data to PostgreSQL.")
