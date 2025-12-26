from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from transformers import pipeline
import json
from contextlib import asynccontextmanager

from app.database import SessionLocal, engine
from app.models import Base, IngredientTaxonomy, ExtractionLog

# NLP Pipeline
ner_pipeline = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model on startup
    global ner_pipeline
    print("Loading NLP Model...")
    try:
        # Use a multilingual NER model
        ner_pipeline = pipeline("ner", model="Davlan/bert-base-multilingual-cased-ner-hrl", aggregation_strategy="simple")
        print("NLP Model loaded.")
    except Exception as e:
        print(f"Error loading model: {e}")
    
    # Init DB
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created.")
    except Exception as e:
        print(f"DB Error: {e}")
        
    yield
    pass

app = FastAPI(title="NLPIngredients", lifespan=lifespan)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "nlp-ingredients"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class IdentificationRequest(BaseModel):
    text: str

class Entity(BaseModel):
    entity_group: str
    word: str
    score: float

class IdentificationResponse(BaseModel):
    entities: list[Entity]
    normalized_ingredients: list[str]

@app.post("/nlp/extract", response_model=IdentificationResponse)
def extract_entities(request: IdentificationRequest, db: Session = Depends(get_db)):
    if not ner_pipeline:
        raise HTTPException(status_code=503, detail="NLP model not loaded")
    
    text = request.text
    # BERT NER extraction
    results = ner_pipeline(text)
    
    # Format entities
    entities = []
    for r in results:
        entities.append(Entity(
            entity_group=r['entity_group'],
            word=r['word'],
            score=float(r['score'])
        ))
    
    # Simple normalization/matching against DB (Mock logic for now)
    # in real app: fuzzy match against IngredientTaxonomy
    ingredients = [e.word for e in entities if e.entity_group in ['ORG', 'MISC', 'PER']] # Simplification
    
    # Save log
    log = ExtractionLog(raw_text=text, extracted_data=json.dumps([e.dict() for e in entities]))
    db.add(log)
    db.commit()
    
    return IdentificationResponse(entities=entities, normalized_ingredients=ingredients)

@app.get("/health")
def health():
    return {"status": "ok"}
