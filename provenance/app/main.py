from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import json
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(
    title="Provenance",
    description="""
    Service de traçabilité et d'audit des calculs EcoLabel.
    
    ## Fonctionnalités
    - Recherche de scores par ID ou nom de produit
    - Historique des calculs LCA
    - Audit complet avec détails des calculs
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

# Database configuration
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "eco")
DB_PASSWORD = os.getenv("DB_PASSWORD", "eco_pass")
DB_NAME = os.getenv("DB_NAME", "eco_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = None
SessionLocal = None

def init_db():
    global engine, SessionLocal
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        print(f"✓ Connected to database: {DB_HOST}:{DB_PORT}/{DB_NAME}")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

@app.on_event("startup")
def startup():
    init_db()

def get_db():
    if SessionLocal is None:
        return None
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health_check():
    db_connected = engine is not None
    return {
        "status": "healthy", 
        "service": "provenance",
        "database_connected": db_connected,
        "version": "2.0.0"
    }


class ScoreResult(BaseModel):
    id: int
    product_name: str
    score_numerical: float
    score_letter: str
    confidence_level: float
    created_at: Optional[str]


class LCAResult(BaseModel):
    id: int
    product_name: str
    total_co2: float
    total_water: float
    total_energy: float
    details: Optional[dict]
    created_at: Optional[str]


class AuditResult(BaseModel):
    score: Optional[ScoreResult]
    lca: Optional[LCAResult]
    audit_timestamp: str
    data_source: str


@app.get("/provenance/{score_id}")
def get_provenance(score_id: str):
    """Get provenance data for a score ID"""
    if engine is None:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        with engine.connect() as conn:
            # Get score from product_scores
            result = conn.execute(
                text("SELECT id, product_name, score_numerical, score_letter, confidence_level, created_at FROM product_scores WHERE id = :id"),
                {"id": int(score_id)}
            )
            score_row = result.fetchone()
            
            if not score_row:
                raise HTTPException(status_code=404, detail=f"Score ID {score_id} not found")
            
            score_data = {
                "id": score_row[0],
                "product_name": score_row[1],
                "score_numerical": float(score_row[2]) if score_row[2] else 0,
                "score_letter": score_row[3],
                "confidence_level": float(score_row[4]) if score_row[4] else 0,
                "created_at": str(score_row[5]) if score_row[5] else None
            }
            
            # Try to find matching LCA result
            lca_result = conn.execute(
                text("SELECT id, product_name, total_co2, total_water, total_energy, details, created_at FROM lca_results WHERE product_name = :name ORDER BY id DESC LIMIT 1"),
                {"name": score_data["product_name"]}
            )
            lca_row = lca_result.fetchone()
            
            lca_data = None
            if lca_row:
                lca_data = {
                    "id": lca_row[0],
                    "product_name": lca_row[1],
                    "total_co2": float(lca_row[2]) if lca_row[2] else 0,
                    "total_water": float(lca_row[3]) if lca_row[3] else 0,
                    "total_energy": float(lca_row[4]) if lca_row[4] else 0,
                    "details": lca_row[5] if lca_row[5] else None,
                    "created_at": str(lca_row[6]) if lca_row[6] else None
                }
            
            return {
                "score": score_data,
                "lca": lca_data,
                "audit_timestamp": datetime.now().isoformat(),
                "data_source": "PostgreSQL"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/provenance/search/{product_name}")
def search_by_product(product_name: str):
    """Search scores by product name"""
    if engine is None:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT id, product_name, score_numerical, score_letter, confidence_level, created_at 
                    FROM product_scores 
                    WHERE LOWER(product_name) LIKE LOWER(:name)
                    ORDER BY created_at DESC
                    LIMIT 20
                """),
                {"name": f"%{product_name}%"}
            )
            
            scores = []
            for row in result.fetchall():
                scores.append({
                    "id": row[0],
                    "product_name": row[1],
                    "score_numerical": float(row[2]) if row[2] else 0,
                    "score_letter": row[3],
                    "confidence_level": float(row[4]) if row[4] else 0,
                    "created_at": str(row[5]) if row[5] else None
                })
            
            return {
                "query": product_name,
                "count": len(scores),
                "results": scores
            }
            
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/provenance/history/scores")
def get_scores_history(limit: int = 20):
    """Get recent scores history"""
    if engine is None:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT id, product_name, score_numerical, score_letter, confidence_level, created_at 
                    FROM product_scores 
                    ORDER BY created_at DESC
                    LIMIT :limit
                """),
                {"limit": limit}
            )
            
            scores = []
            for row in result.fetchall():
                scores.append({
                    "id": row[0],
                    "product_name": row[1],
                    "score_numerical": float(row[2]) if row[2] else 0,
                    "score_letter": row[3],
                    "confidence_level": float(row[4]) if row[4] else 0,
                    "created_at": str(row[5]) if row[5] else None
                })
            
            return {
                "count": len(scores),
                "scores": scores
            }
            
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/provenance/history/lca")
def get_lca_history(limit: int = 20):
    """Get recent LCA calculations history"""
    if engine is None:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT id, product_name, total_co2, total_water, total_energy, created_at 
                    FROM lca_results 
                    ORDER BY created_at DESC
                    LIMIT :limit
                """),
                {"limit": limit}
            )
            
            results = []
            for row in result.fetchall():
                results.append({
                    "id": row[0],
                    "product_name": row[1],
                    "total_co2": float(row[2]) if row[2] else 0,
                    "total_water": float(row[3]) if row[3] else 0,
                    "total_energy": float(row[4]) if row[4] else 0,
                    "created_at": str(row[5]) if row[5] else None
                })
            
            return {
                "count": len(results),
                "lca_results": results
            }
            
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/provenance/stats")
def get_stats():
    """Get statistics from all microservices data"""
    if engine is None:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        with engine.connect() as conn:
            stats = {}
            
            # Product scores stats
            result = conn.execute(text("SELECT COUNT(*), AVG(score_numerical) FROM product_scores"))
            row = result.fetchone()
            stats["scores"] = {
                "count": row[0] if row[0] else 0,
                "avg_score": round(float(row[1]), 2) if row[1] else 0
            }
            
            # Score distribution
            result = conn.execute(text("""
                SELECT score_letter, COUNT(*) as count 
                FROM product_scores 
                GROUP BY score_letter 
                ORDER BY score_letter
            """))
            stats["score_distribution"] = {row[0]: row[1] for row in result.fetchall()}
            
            # LCA results stats
            result = conn.execute(text("SELECT COUNT(*), AVG(total_co2), AVG(total_water), AVG(total_energy) FROM lca_results"))
            row = result.fetchone()
            stats["lca"] = {
                "count": row[0] if row[0] else 0,
                "avg_co2": round(float(row[1]), 3) if row[1] else 0,
                "avg_water": round(float(row[2]), 2) if row[2] else 0,
                "avg_energy": round(float(row[3]), 2) if row[3] else 0
            }
            
            # Products parsed
            result = conn.execute(text("SELECT COUNT(*) FROM product_raw"))
            row = result.fetchone()
            stats["products_parsed"] = row[0] if row[0] else 0
            
            # Emission factors
            result = conn.execute(text("SELECT COUNT(*) FROM emission_factors"))
            row = result.fetchone()
            stats["emission_factors"] = row[0] if row[0] else 0
            
            return stats
            
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
