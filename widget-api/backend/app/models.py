from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# We only need read access to product_scores largely, but let's define the model
class ProductScore(Base):
    __tablename__ = "product_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    score_numerical = Column(Float)
    score_letter = Column(String(1)) # A, B, C, D, E
    confidence_level = Column(Float)
    created_at = Column(DateTime)
