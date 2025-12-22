from pydantic import BaseModel
from typing import Optional, List

class ProductParsed(BaseModel):
    id: int
    gtin: Optional[str]
    raw_text: str

    class Config:
        from_attributes = True
