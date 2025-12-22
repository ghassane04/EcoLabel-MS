from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import pandas as pd
import json
import io
import datetime
from database import SessionLocal, engine, minio_client
from models import Base, EmissionFactor, LCAResult

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

# App
app = FastAPI(title="LCA-Lite")

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

def ensure_minio_bucket():
    bucket_name = "lca-reports"
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
    return bucket_name

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    # Seed data if empty (simplified for demo)
    db = SessionLocal()
    if db.query(EmissionFactor).count() == 0:
        factors = [
            EmissionFactor(name="tomato", category="ingredient", co2_factor=1.5, water_factor=50.0, energy_factor=2.0),
            EmissionFactor(name="sugar", category="ingredient", co2_factor=0.8, water_factor=200.0, energy_factor=5.0),
            EmissionFactor(name="plastic", category="packaging", co2_factor=3.0, water_factor=10.0, energy_factor=40.0),
            EmissionFactor(name="glass", category="packaging", co2_factor=0.9, water_factor=5.0, energy_factor=15.0),
            EmissionFactor(name="transport_km", category="transport", co2_factor=0.0001, water_factor=0.0, energy_factor=0.005),
        ]
        db.add_all(factors)
        db.commit()
    db.close()
    try:
        ensure_minio_bucket()
    except Exception as e:
        print(f"MinIO Warning: {e}")

@app.post("/lca/calc", response_model=LCACalculationResponse)
def calculate_lca(request: LCACalculationRequest, db: Session = Depends(get_db)):
    try:
        # 1. Fetch factors
        factors = {f.name: f for f in db.query(EmissionFactor).all()}
        transport_factor = factors.get("transport_km")
        
        # 2. DataFrame for Ingredients
        ing_data = []
        for ing in request.ingredients:
            f = factors.get(ing.name, EmissionFactor(co2_factor=1.0, water_factor=10.0, energy_factor=5.0)) # Defaults
            ing_data.append({
                "component": ing.name,
                "type": "ingredient",
                "quantity": ing.quantity_kg,
                "co2": ing.quantity_kg * f.co2_factor,
                "water": ing.quantity_kg * f.water_factor,
                "energy": ing.quantity_kg * f.energy_factor
            })
            
        # 3. Packaging
        pkg = request.packaging
        f_pkg = factors.get(pkg.material, EmissionFactor(co2_factor=2.0, water_factor=10.0, energy_factor=20.0))
        ing_data.append({
            "component": pkg.material,
            "type": "packaging",
            "quantity": pkg.weight_kg,
            "co2": pkg.weight_kg * f_pkg.co2_factor,
            "water": pkg.weight_kg * f_pkg.water_factor,
            "energy": pkg.weight_kg * f_pkg.energy_factor
        })
        
        # 4. Transport (Simulated as global adder based on total weight?)
        # Or just simple distance based. Let's do simple distance assuming 1kg unit for simplicity or loop over items.
        # Specification says "Ingredients + transport". Let's assume transport applies to the whole product weight.
        total_weight = sum(item['quantity'] for item in ing_data)
        dist = request.transport.distance_km
        if transport_factor:
            t_co2 = dist * total_weight * transport_factor.co2_factor
            t_energy = dist * total_weight * transport_factor.energy_factor
        else:
            t_co2 = 0
            t_energy = 0
            
        ing_data.append({
            "component": "transport",
            "type": "transport",
            "quantity": dist,
            "co2": t_co2,
            "water": 0,
            "energy": t_energy
        })
        
        df = pd.DataFrame(ing_data)
        
        # Aggregates
        totals = df[["co2", "water", "energy"]].sum()
        
        # 5. Save Report to MinIO
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

        # 6. Save Result to DB
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
            breakdown={"items": breakdown}
        )
    except Exception as e:
        print(f"ERROR IN CALCULATION: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
