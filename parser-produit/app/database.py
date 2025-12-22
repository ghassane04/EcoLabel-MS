from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Use individual components to avoid URL encoding issues on Windows
DB_USER = os.getenv("DB_USER", "eco")
DB_PASSWORD = os.getenv("DB_PASSWORD", "eco_pass")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "eco_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"options": "-c client_encoding=utf8"}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
