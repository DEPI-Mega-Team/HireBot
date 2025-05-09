from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import pymssql
import os

load_dotenv()

# Create the database directory if it doesn't exist
os.makedirs('database', exist_ok=True)

# SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///database/interview.db"

# Create engine with SQLite specific configuration
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)
SessionLocal = sessionmaker(
                            autocommit= False,
                            autoflush= False,
                            bind= engine,
                            )

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 


# Connect to MS SQL Server
DB_SERVER= os.environ.get('DB_SERVER')
DB_DATABASE = os.environ.get('DB_DATABASE')
DB_USER_ID = os.environ.get('DB_USER_ID')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_PORT = os.environ.get('DB_PORT')

def get_mssql_connection():
    return pymssql.connect(server=DB_SERVER, port=DB_PORT, user=DB_USER_ID, password=DB_PASSWORD, database=DB_DATABASE)