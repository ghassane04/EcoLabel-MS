from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import pandas as pd
import json
import io
import datetime
import os
from app.database import SessionLocal, engine, minio_client
from app.models import Base, EmissionFactor, LCAResult

# Try to import ML imputer
try:
    from app.ml_imputer import load_co2_model, estimate_co2, train_co2_model
    ML_AVAILABLE = True
except ImportError as e:
    print(f"ML imputer not available: {e}")
    ML_AVAILABLE = False

# Schemas
class IngredientInput(BaseModel):
    name: str # e.g. "tomato"
    quantity_kg: float

class PackagingInput(BaseModel):
    material: str # e.g. "plastic", "glass"
    weight_kg: float

class TransportInput(BaseModel):
    distance_km: float
    mode: str # "truck", "ship" (default simplified)

class LCACalculationRequest(BaseModel):
    product_name: str
    ingredients: list[IngredientInput]
    packaging: PackagingInput
    transport: TransportInput

class LCACalculationResponse(BaseModel):
    product_name: str
    total_co2_kg: float
    total_water_l: float
    total_energy_mj: float
    breakdown: dict
    ml_imputation_used: bool = False

# App
app = FastAPI(
    title="LCA-Lite (ML-Enhanced)",
    description="""
    Service de calcul d'Analyse de Cycle de Vie.
    
    ## Fonctionnalités
    - Calcul ACV basé sur facteurs d'émission
    - **Imputation ML** : Estimation CO₂ par XGBoost quand ingrédients inconnus
    - Stockage rapports MinIO
    """,
    version="2.0.0"
)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ML state
ml_model_loaded = False
imputer_metrics = None

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "service": "lca-lite",
        "ml_imputer_available": ML_AVAILABLE and ml_model_loaded,
        "version": "2.0.0"
    }

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def ensure_minio_bucket():
    bucket_name = "lca-reports"
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
    return bucket_name

def load_ml_imputer():
    """Load the ML imputer model"""
    global ml_model_loaded, imputer_metrics
    
    if not ML_AVAILABLE:
        print("✗ ML imputer module not available")
        return
    
    try:
        # Check if model exists, if not train it
        model_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'co2_imputer.pkl')
        metrics_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'imputer_metrics.json')
        
        if not os.path.exists(model_path):
            print("Training new CO₂ imputer model...")
            train_co2_model(verbose=False)
        
        # Load model to verify
        load_co2_model()
        ml_model_loaded = True
        
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r') as f:
                imputer_metrics = json.load(f)
            r2 = imputer_metrics.get('metrics', {}).get('r2_score', 0)
            print(f"✓ ML Imputer loaded (R² = {r2:.3f})")
        else:
            print("✓ ML Imputer loaded")
            
    except Exception as e:
        print(f"✗ Error loading ML imputer: {e}")
        ml_model_loaded = False

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    
    # Seed data if empty
    db = SessionLocal()
    if db.query(EmissionFactor).count() == 0:
        factors = [
            # Vegetables (low impact)
            EmissionFactor(name="tomato", category="ingredient", co2_factor=1.5, water_factor=50.0, energy_factor=2.0),
            EmissionFactor(name="tomates_bio_italiennes", category="ingredient", co2_factor=1.2, water_factor=45.0, energy_factor=1.8),
            EmissionFactor(name="salade_verte_bio_locale", category="ingredient", co2_factor=0.3, water_factor=20.0, energy_factor=0.5),
            EmissionFactor(name="basilic_frais", category="ingredient", co2_factor=0.5, water_factor=30.0, energy_factor=0.8),
            EmissionFactor(name="sauce_tomate", category="ingredient", co2_factor=2.0, water_factor=60.0, energy_factor=3.0),
            EmissionFactor(name="carrot", category="ingredient", co2_factor=0.4, water_factor=25.0, energy_factor=0.6),
            EmissionFactor(name="potato", category="ingredient", co2_factor=0.5, water_factor=35.0, energy_factor=0.8),
            EmissionFactor(name="onion", category="ingredient", co2_factor=0.3, water_factor=20.0, energy_factor=0.5),
            
            # Oils (medium impact)
            EmissionFactor(name="huile_d'olive_extra_vierge", category="ingredient", co2_factor=3.0, water_factor=100.0, energy_factor=8.0),
            EmissionFactor(name="huile_d'olive_bio", category="ingredient", co2_factor=2.5, water_factor=90.0, energy_factor=7.0),
            
            # Condiments (low impact)
            EmissionFactor(name="sugar", category="ingredient", co2_factor=0.8, water_factor=200.0, energy_factor=5.0),
            EmissionFactor(name="sel_de_mer", category="ingredient", co2_factor=0.2, water_factor=5.0, energy_factor=0.5),
            EmissionFactor(name="flour", category="ingredient", co2_factor=0.7, water_factor=150.0, energy_factor=4.0),
            
            # Dairy (medium-high impact)
            EmissionFactor(name="milk", category="ingredient", co2_factor=3.2, water_factor=250.0, energy_factor=8.0),
            EmissionFactor(name="cheese", category="ingredient", co2_factor=8.0, water_factor=500.0, energy_factor=20.0),
            EmissionFactor(name="butter", category="ingredient", co2_factor=9.0, water_factor=400.0, energy_factor=18.0),
            EmissionFactor(name="fromage_industriel", category="ingredient", co2_factor=8.0, water_factor=500.0, energy_factor=20.0),
            
            # Meat (HIGH impact)
            EmissionFactor(name="viande_de_boeuf", category="ingredient", co2_factor=25.0, water_factor=1500.0, energy_factor=50.0),
            EmissionFactor(name="beef", category="ingredient", co2_factor=25.0, water_factor=1500.0, energy_factor=50.0),
            EmissionFactor(name="chicken", category="ingredient", co2_factor=6.0, water_factor=400.0, energy_factor=15.0),
            EmissionFactor(name="pork", category="ingredient", co2_factor=7.0, water_factor=600.0, energy_factor=18.0),
            EmissionFactor(name="pâte_industrielle", category="ingredient", co2_factor=3.0, water_factor=200.0, energy_factor=10.0),
            
            # Packaging
            EmissionFactor(name="plastic", category="packaging", co2_factor=6.0, water_factor=30.0, energy_factor=80.0),
            EmissionFactor(name="glass", category="packaging", co2_factor=0.9, water_factor=5.0, energy_factor=15.0),
            EmissionFactor(name="paper", category="packaging", co2_factor=0.3, water_factor=10.0, energy_factor=5.0),
            EmissionFactor(name="cardboard", category="packaging", co2_factor=0.4, water_factor=12.0, energy_factor=6.0),
            EmissionFactor(name="aluminum", category="packaging", co2_factor=8.0, water_factor=40.0, energy_factor=100.0),
            
            # Transport (per km per kg)
            EmissionFactor(name="transport_km", category="transport", co2_factor=0.0001, water_factor=0.0, energy_factor=0.005),
            EmissionFactor(name="transport_air", category="transport", co2_factor=0.001, water_factor=0.0, energy_factor=0.05),
            EmissionFactor(name="transport_bike", category="transport", co2_factor=0.00001, water_factor=0.0, energy_factor=0.0001),
        ]
        db.add_all(factors)
        db.commit()
    db.close()
    
    try:
        ensure_minio_bucket()
    except Exception as e:
        print(f"MinIO Warning: {e}")
    
    # Load ML imputer
    load_ml_imputer()


def detect_ingredient_types(ingredients: list, factors: dict) -> dict:
    """Detect ingredient types for ML imputation"""
    has_meat = False
    has_dairy = False
    has_vegetables = False
    
    meat_keywords = ['beef', 'chicken', 'pork', 'meat', 'viande', 'boeuf', 'poulet', 'porc']
    dairy_keywords = ['milk', 'cheese', 'butter', 'cream', 'lait', 'fromage', 'beurre']
    vegetable_keywords = ['tomato', 'carrot', 'potato', 'onion', 'salad', 'vegetable', 'légume', 'tomate']
    
    for ing in ingredients:
        name_lower = ing.name.lower()
        
        # Check known factors
        if ing.name in factors:
            factor = factors[ing.name]
            if hasattr(factor, 'co2_factor'):
                if factor.co2_factor >= 6.0:
                    has_meat = True
                elif factor.co2_factor >= 3.0:
                    has_dairy = True
                else:
                    has_vegetables = True
        
        # Check keywords
        for kw in meat_keywords:
            if kw in name_lower:
                has_meat = True
                break
        for kw in dairy_keywords:
            if kw in name_lower:
                has_dairy = True
                break
        for kw in vegetable_keywords:
            if kw in name_lower:
                has_vegetables = True
                break
    
    return {
        'has_meat': has_meat,
        'has_dairy': has_dairy,
        'has_vegetables': has_vegetables
    }


@app.post("/lca/calc", response_model=LCACalculationResponse)
def calculate_lca(request: LCACalculationRequest, db: Session = Depends(get_db)):
    try:
        # 1. Fetch factors
        factors = {f.name: f for f in db.query(EmissionFactor).all()}
        transport_factor = factors.get("transport_km")
        
        # Track if we use ML imputation
        ml_imputation_used = False
        unknown_ingredients = []
        
        # 2. DataFrame for Ingredients
        ing_data = []
        total_weight = 0
        
        for ing in request.ingredients:
            total_weight += ing.quantity_kg
            
            if ing.name in factors:
                f = factors[ing.name]
                ing_data.append({
                    "component": ing.name,
                    "type": "ingredient",
                    "quantity": ing.quantity_kg,
                    "co2": ing.quantity_kg * f.co2_factor,
                    "water": ing.quantity_kg * f.water_factor,
                    "energy": ing.quantity_kg * f.energy_factor,
                    "source": "database"
                })
            else:
                unknown_ingredients.append(ing)
                # Use default values for now, will be updated by ML
                ing_data.append({
                    "component": ing.name,
                    "type": "ingredient",
                    "quantity": ing.quantity_kg,
                    "co2": ing.quantity_kg * 1.0,  # Default
                    "water": ing.quantity_kg * 10.0,
                    "energy": ing.quantity_kg * 5.0,
                    "source": "default"
                })
        
        # 3. If we have unknown ingredients, use ML imputation for total CO₂ estimation
        if unknown_ingredients and ML_AVAILABLE and ml_model_loaded:
            try:
                ingredient_types = detect_ingredient_types(request.ingredients, factors)
                
                ml_result = estimate_co2(
                    num_ingredients=len(request.ingredients),
                    total_weight_kg=total_weight + request.packaging.weight_kg,
                    has_meat=ingredient_types['has_meat'],
                    has_dairy=ingredient_types['has_dairy'],
                    has_vegetables=ingredient_types['has_vegetables'],
                    packaging_type=request.packaging.material,
                    packaging_weight_kg=request.packaging.weight_kg,
                    transport_km=request.transport.distance_km
                )
                
                # Calculate how much CO₂ we've already accounted for
                known_co2 = sum(item['co2'] for item in ing_data if item['source'] == 'database')
                estimated_total_co2 = ml_result['co2_kg']
                
                # Distribute remaining CO₂ to unknown ingredients proportionally by weight
                remaining_co2 = max(0, estimated_total_co2 - known_co2)
                unknown_total_weight = sum(ing.quantity_kg for ing in unknown_ingredients)
                
                if unknown_total_weight > 0:
                    for item in ing_data:
                        if item['source'] == 'default':
                            proportion = item['quantity'] / unknown_total_weight
                            item['co2'] = remaining_co2 * proportion
                            item['source'] = 'ml_estimated'
                    
                    ml_imputation_used = True
                    print(f"ML Imputation: Estimated total CO₂ = {estimated_total_co2:.2f}kg (confidence: {ml_result['confidence']:.0%})")
                    
            except Exception as e:
                print(f"ML imputation failed: {e}")
        
        # 4. Packaging
        pkg = request.packaging
        f_pkg = factors.get(pkg.material, EmissionFactor(co2_factor=2.0, water_factor=10.0, energy_factor=20.0))
        ing_data.append({
            "component": pkg.material,
            "type": "packaging",
            "quantity": pkg.weight_kg,
            "co2": pkg.weight_kg * f_pkg.co2_factor,
            "water": pkg.weight_kg * f_pkg.water_factor,
            "energy": pkg.weight_kg * f_pkg.energy_factor,
            "source": "database" if pkg.material in factors else "default"
        })
        
        # 5. Transport
        total_weight_with_pkg = total_weight + pkg.weight_kg
        dist = request.transport.distance_km
        if transport_factor:
            t_co2 = dist * total_weight_with_pkg * transport_factor.co2_factor
            t_energy = dist * total_weight_with_pkg * transport_factor.energy_factor
        else:
            t_co2 = 0
            t_energy = 0
            
        ing_data.append({
            "component": "transport",
            "type": "transport",
            "quantity": dist,
            "co2": t_co2,
            "water": 0,
            "energy": t_energy,
            "source": "database"
        })
        
        df = pd.DataFrame(ing_data)
        
        # Aggregates
        totals = df[["co2", "water", "energy"]].sum()
        
        # 6. Save Report to MinIO
        report_content = df.to_csv(index=False)
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{request.product_name}_{timestamp}.csv"
        try:
            minio_client.put_object(
                "lca-reports",
                filename,
                io.BytesIO(report_content.encode('utf-8')),
                len(report_content),
                content_type="text/csv"
            )
        except Exception as e:
            print(f"Failed to save to MinIO: {e}")

        # 7. Save Result to DB
        breakdown = df.to_dict(orient="records")
        result_db = LCAResult(
            product_name=request.product_name,
            total_co2=float(totals["co2"]),
            total_water=float(totals["water"]),
            total_energy=float(totals["energy"]),
            details=breakdown
        )
        db.add(result_db)
        db.commit()
        
        return LCACalculationResponse(
            product_name=request.product_name,
            total_co2_kg=float(totals["co2"]),
            total_water_l=float(totals["water"]),
            total_energy_mj=float(totals["energy"]),
            breakdown={
                "items": breakdown,
                "ml_imputation": ml_imputation_used
            },
            ml_imputation_used=ml_imputation_used
        )
    except Exception as e:
        print(f"ERROR IN CALCULATION: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/lca/model-info")
def get_model_info():
    """Return information about the ML imputer model"""
    if imputer_metrics:
        return {
            "ml_available": ML_AVAILABLE,
            "model_loaded": ml_model_loaded,
            "model": imputer_metrics.get('model'),
            "metrics": imputer_metrics.get('metrics'),
            "feature_importance": imputer_metrics.get('feature_importance'),
            "trained_at": imputer_metrics.get('trained_at')
        }
    return {
        "ml_available": ML_AVAILABLE,
        "model_loaded": ml_model_loaded,
        "message": "No imputer metrics available"
    }


@app.post("/lca/train-imputer")
async def train_imputer():
    """Train or retrain the CO₂ imputer model"""
    if not ML_AVAILABLE:
        raise HTTPException(status_code=500, detail="ML imputer module not available")
    
    try:
        global ml_model_loaded, imputer_metrics
        _, imputer_metrics = train_co2_model(verbose=False)
        ml_model_loaded = True
        
        return {
            "status": "success",
            "message": "CO₂ imputer trained successfully",
            "r2_score": imputer_metrics.get('metrics', {}).get('r2_score'),
            "mae": imputer_metrics.get('metrics', {}).get('mae')
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")
