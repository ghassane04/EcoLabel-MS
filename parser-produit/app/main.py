from fastapi import FastAPI, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
import pytesseract
from PIL import Image
from bs4 import BeautifulSoup
import sys
import io
from contextlib import asynccontextmanager

# Fix for Windows UTF-8 encoding issues with psycopg2
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        from app.database import SessionLocal, engine
        from app.models import Base
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Warning: Could not connect to database: {e}")
        print("The app will start but database operations will fail")
    yield
    # Shutdown
    pass

app = FastAPI(title="ParserProduit", lifespan=lifespan)

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
    return {"status": "healthy", "service": "parser-produit"}

# Import after app creation to avoid issues
from app.database import SessionLocal
from app.models import ProductRaw
from app.schemas import ProductParsed

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/product/parse", response_model=list[ProductParsed])
async def parse_products(
    files: list[UploadFile] = File(...),
    gtin: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    results = []
    for f in files:
        content = await f.read()
        if f.content_type.startswith("image/"):
            image = Image.open(io.BytesIO(content))
            text = pytesseract.image_to_string(image)
            source_type = "image"
        elif f.filename.endswith(".html"):
            soup = BeautifulSoup(content, "html.parser")
            text = soup.get_text(separator="\n")
            source_type = "html"
        else:
            text = content.decode(errors="ignore")
            source_type = "pdf"
        obj = ProductRaw(gtin=gtin, source_type=source_type, raw_text=text)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        results.append(obj)
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
