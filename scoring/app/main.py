"""
Scoring Microservice with ML-Based Predictions
Uses XGBoost or Random Forest model for eco-score classification
"""

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Dict, Optional
import numpy as np
import os
import json

from app.database import SessionLocal, engine
from app.models import Base, ProductScore

# Try to import ML components
try:
    from app.ml_trainer import load_model, predict as ml_predict_func, train_models
    ML_AVAILABLE = True
except ImportError as e:
    print(f"ML trainer not available: {e}")
    ML_AVAILABLE = False

# ============ CONFIGURATION ============
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'scoring_model.pkl')
METRICS_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'training_metrics.json')

# Score values for probability-weighted scoring
SCORE_VALUES = {'A': 95, 'B': 75, 'C': 55, 'D': 35, 'E': 15}

# ============ INIT DB ============
Base.metadata.create_all(bind=engine)

# ============ ML STATE ============
ml_model_bundle = None
training_metrics = None

def load_ml_model():
    global ml_model_bundle, training_metrics
    
    if not ML_AVAILABLE:
        print("✗ ML trainer not available")
        return False
    
    try:
        ml_model_bundle = load_model()
        model_name = ml_model_bundle.get('model_name', 'Unknown')
        print(f"✓ ML Model loaded: {model_name}")
        
        if os.path.exists(METRICS_PATH):
            with open(METRICS_PATH, 'r') as f:
                training_metrics = json.load(f)
            accuracy = training_metrics.get('best_model_metrics', {}).get('test_accuracy', 0)
            print(f"✓ Accuracy: {accuracy:.2%}")
        
        return True
    except Exception as e:
        print(f"✗ Error loading ML model: {e}")
        # Try to train a new model
        print("  Attempting to train new model...")
        try:
            ml_model_bundle, training_metrics = train_models(verbose=False)
            print(f"✓ New model trained: {ml_model_bundle['model_name']}")
            return True
        except Exception as e2:
            print(f"✗ Training failed: {e2}")
    
    return False

# ============ CREATE APP ============
app = FastAPI(
    title="Scoring EcoLabel (ML-Powered)",
    description="""
    Service de scoring environnemental utilisant Machine Learning.
    
    ## Algorithme
    - **Modèle**: XGBoost ou Random Forest (sélection automatique)
    - **Dataset**: 500 échantillons équilibrés
    - **Features**: CO₂, eau, énergie, emballage, transport, labels
    - **Sortie**: Score A-E avec probabilités et confiance
    """,
    version="3.0.0"
)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model on startup
@app.on_event("startup")
def startup():
    load_ml_model()

# ============ DB DEPENDENCY ============
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============ PYDANTIC MODELS ============
class ScoreRequest(BaseModel):
    product_name: str
    total_co2: float
    total_water: float
    total_energy: float
    packaging_type: str = "plastic"
    packaging_weight_kg: float = 0.3
    transport_km: float = 200
    has_bio_label: int = 0
    has_recyclable: int = 0
    has_local_label: int = 0
    category: str = "processed"
    # Legacy fields for backward compatibility
    max_co2_ref: float = 10.0
    max_water_ref: float = 500.0
    max_energy_ref: float = 50.0

class ScoreResponse(BaseModel):
    product_name: str
    score_numerical: float
    score_letter: str
    confidence_level: float
    explanation: str
    probabilities: Optional[Dict[str, float]] = None
    model_used: str = "rule-based"

# ============ SCORING LOGIC ============

def ml_predict(request: ScoreRequest) -> Dict:
    """Use ML model for prediction"""
    if ml_model_bundle is None or not ML_AVAILABLE:
        return None
    
    try:
        result = ml_predict_func(
            co2_kg=request.total_co2,
            water_l=request.total_water,
            energy_mj=request.total_energy,
            packaging_type=request.packaging_type,
            packaging_weight_kg=request.packaging_weight_kg,
            transport_km=request.transport_km,
            has_bio_label=request.has_bio_label,
            has_recyclable=request.has_recyclable,
            has_local_label=request.has_local_label,
            category=request.category
        )
        
        # Calculate numerical score from probabilities
        score_num = sum(SCORE_VALUES.get(c, 50) * p for c, p in result['probabilities'].items())
        
        return {
            'letter': result['grade'],
            'score': round(score_num, 1),
            'proba': result['probabilities'],
            'confidence': result['confidence'],
            'model_name': result['model_name']
        }
    except Exception as e:
        print(f"ML prediction error: {e}")
        import traceback
        traceback.print_exc()
        return None


def rule_based_predict(request: ScoreRequest) -> Dict:
    """Fallback rule-based scoring"""
    # Normalize inputs relative to reference values
    norm_co2 = min(request.total_co2 / request.max_co2_ref, 1.0)
    norm_water = min(request.total_water / request.max_water_ref, 1.0)
    norm_energy = min(request.total_energy / request.max_energy_ref, 1.0)
    
    # Weights (CO₂ most important)
    w_co2 = 0.50
    w_water = 0.25
    w_energy = 0.25
    
    # Calculate score (100 = best, 0 = worst)
    raw_score = (norm_co2 * w_co2) + (norm_water * w_water) + (norm_energy * w_energy)
    score_num = 100 - (raw_score * 100)
    
    # Apply bonuses for labels
    if request.has_bio_label:
        score_num += 5
    if request.has_recyclable:
        score_num += 3
    if request.has_local_label:
        score_num += 5
    
    # Clamp to 0-100
    score_num = max(0, min(100, score_num))
    
    # Determine letter
    if score_num >= 80:
        letter = 'A'
    elif score_num >= 60:
        letter = 'B'
    elif score_num >= 40:
        letter = 'C'
    elif score_num >= 20:
        letter = 'D'
    else:
        letter = 'E'
    
    return {
        'letter': letter,
        'score': round(score_num, 1),
        'proba': None,
        'confidence': 0.7,
        'model_name': 'rule-based'
    }


# ============ ENDPOINTS ============

@app.get("/health")
def health_check():
    model_name = ml_model_bundle.get('model_name') if ml_model_bundle else None
    return {
        "status": "healthy",
        "service": "scoring",
        "ml_model_loaded": ml_model_bundle is not None,
        "model_type": model_name or "rule-based",
        "version": "3.0.0"
    }


@app.post("/score/compute", response_model=ScoreResponse)
def compute_score(request: ScoreRequest, db: Session = Depends(get_db)):
    """
    Calcule le score environnemental d'un produit.
    
    Utilise le modèle ML (XGBoost/RandomForest) si disponible, sinon formule pondérée.
    """
    # Try ML prediction first
    result = ml_predict(request)
    
    # Fallback to rules if ML fails
    if result is None:
        result = rule_based_predict(request)
    
    model_used = result.get('model_name', 'rule-based')
    
    # Build explanation
    explanation = (
        f"Score {result['letter']} ({result['score']}/100) calculé par {model_used}. "
        f"Basé sur CO₂={request.total_co2}kg, Eau={request.total_water}L, "
        f"Énergie={request.total_energy}MJ, Transport={request.transport_km}km, "
        f"Emballage={request.packaging_type}."
    )
    
    # Save to DB
    db_score = ProductScore(
        product_name=request.product_name,
        score_numerical=result['score'],
        score_letter=result['letter'],
        confidence_level=result['confidence']
    )
    db.add(db_score)
    db.commit()
    
    return ScoreResponse(
        product_name=request.product_name,
        score_numerical=result['score'],
        score_letter=result['letter'],
        confidence_level=result['confidence'],
        explanation=explanation,
        probabilities=result['proba'],
        model_used=model_used
    )


@app.get("/score/model-info")
def get_model_info():
    """Retourne les informations sur le modèle ML"""
    if training_metrics:
        return {
            "model_loaded": ml_model_bundle is not None,
            "best_model": training_metrics.get('best_model'),
            "dataset_size": training_metrics.get('dataset_size'),
            "models_comparison": training_metrics.get('models_comparison'),
            "best_model_metrics": training_metrics.get('best_model_metrics'),
            "trained_at": training_metrics.get('trained_at')
        }
    return {
        "model_loaded": False,
        "message": "No trained model available. Using rule-based scoring."
    }


@app.post("/score/train")
async def trigger_training():
    """Déclenche l'entraînement du modèle ML (XGBoost + Random Forest)"""
    if not ML_AVAILABLE:
        raise HTTPException(status_code=500, detail="ML trainer not available")
    
    try:
        global ml_model_bundle, training_metrics
        ml_model_bundle, training_metrics = train_models(verbose=False)
        
        return {
            "status": "success",
            "message": f"Model trained successfully: {ml_model_bundle['model_name']}",
            "best_model": training_metrics.get('best_model'),
            "accuracy": training_metrics.get('best_model_metrics', {}).get('test_accuracy'),
            "models_comparison": training_metrics.get('models_comparison')
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")
