from sqlalchemy import Column, Integer, String, Float, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class EmissionFactor(Base):
    __tablename__ = "emission_factors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category = Column(String) # ingredient, packaging, transport
    co2_factor = Column(Float) # kg CO2e per unit
    water_factor = Column(Float) # L water per unit
    energy_factor = Column(Float) # MJ energy per unit

class LCAResult(Base):
    __tablename__ = "lca_results"
    
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String)
    total_co2 = Column(Float)
    total_water = Column(Float)
    total_energy = Column(Float)
    details = Column(JSON) # Store breakdown
