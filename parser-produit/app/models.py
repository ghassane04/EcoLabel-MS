from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ProductRaw(Base):
    __tablename__ = "product_raw"

    id = Column(Integer, primary_key=True, index=True)
    gtin = Column(String(50), index=True, nullable=True)
    source_type = Column(String(20))  # pdf/html/image
    raw_text = Column(Text, nullable=False)
