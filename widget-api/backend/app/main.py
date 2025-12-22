from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import SessionLocal
from models import ProductScore

app = FastAPI(title="WidgetAPI")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for demo
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

@app.get("/public/product/{name}")
def get_product_score(name: str, db: Session = Depends(get_db)):
    # Get latest score for product
    score = db.query(ProductScore).filter(ProductScore.product_name == name).order_by(desc(ProductScore.id)).first()
    if not score:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "product_name": score.product_name,
        "score_letter": score.score_letter,
        "score_numerical": score.score_numerical,
        "confidence": score.confidence_level,
        "created_at": score.created_at
    }

@app.get("/public/products")
def list_products(db: Session = Depends(get_db)):
    # List unique products with latest score
    # Simplified: just return all scores
    scores = db.query(ProductScore).order_by(desc(ProductScore.id)).limit(10).all()
    return scores
