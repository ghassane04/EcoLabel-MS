from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from database import SessionLocal, engine
from models import Base, ProductScore

# Init DB
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Scoring")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ScoreRequest(BaseModel):
    product_name: str
    total_co2: float
    total_water: float
    total_energy: float
    # normalization bounds could be passed or hardcoded based on product category in a real system
    max_co2_ref: float = 10.0 
    max_water_ref: float = 500.0
    max_energy_ref: float = 50.0

class ScoreResponse(BaseModel):
    product_name: str
    score_numerical: float
    score_letter: str
    confidence_level: float
    explanation: str

def calculate_letter_score(numerical_score):
    # Score 0 (Best) to 100 (Worst) mapping similar to Nutri-Score but for Eco
    # Let's assume normalized score is 0-1 where 0 is best.
    # We'll map to 0-100 scale for letter.
    s = numerical_score * 100
    if s < 20: return "A"
    if s < 40: return "B"
    if s < 60: return "C"
    if s < 80: return "D"
    return "E"

@app.post("/score/compute", response_model=ScoreResponse)
def compute_score(request: ScoreRequest, db: Session = Depends(get_db)):
    # Simple weighted sum approach using scikit-learn style normalization manually for single sample
    # In a real batch system we would use scaler.fit_transform on a dataset
    
    # 1. Normalize inputs relative to reference values (Clamping at 1.0)
    norm_co2 = min(request.total_co2 / request.max_co2_ref, 1.0)
    norm_water = min(request.total_water / request.max_water_ref, 1.0)
    norm_energy = min(request.total_energy / request.max_energy_ref, 1.0)
    
    # Weights (Carbon footprint usually has highest weight)
    w_co2 = 0.50
    w_water = 0.25
    w_energy = 0.25
    
    # 2. Compute numerical score (0 to 1, where 0 is best if raw values were 0)
    # Wait, EcoScore usually: Lower impact = Better.
    # So 0.0 is best, 1.0 is worst (max ref).
    score_num = (norm_co2 * w_co2) + (norm_water * w_water) + (norm_energy * w_energy)
    
    # 3. Letter
    letter = calculate_letter_score(score_num)
    
    # 4. Confidence (Mock calculation based on completeness of data?)
    # For now, simplistic
    confidence = 0.9 if request.total_co2 > 0 else 0.5
    
    # Save
    db_score = ProductScore(
        product_name=request.product_name,
        score_numerical=score_num,
        score_letter=letter,
        confidence_level=confidence
    )
    db.add(db_score)
    db.commit()
    
    return ScoreResponse(
        product_name=request.product_name,
        score_numerical=round(score_num * 100, 1), # Return formatted 0-100
        score_letter=letter,
        confidence_level=confidence,
        explanation=f"Based on CO2 ({request.total_co2}kg), Water ({request.total_water}L), Energy ({request.total_energy}MJ). Normalized Score: {score_num:.2f}"
    )
