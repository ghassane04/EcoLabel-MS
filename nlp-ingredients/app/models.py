from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class IngredientTaxonomy(Base):
    __tablename__ = "ingredient_taxonomy"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category = Column(String)  # e.g., 'preservative', 'emulsifier'
    impact_factor = Column(Float, default=0.0) # Placeholder for environmental score

class ExtractionLog(Base):
    __tablename__ = "extraction_log"
    
    id = Column(Integer, primary_key=True, index=True)
    raw_text = Column(String)
    extracted_data = Column(String) # JSON string representation
