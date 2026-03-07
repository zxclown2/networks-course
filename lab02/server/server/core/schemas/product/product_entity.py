from pydantic import BaseModel, Field

from typing import Optional

class Product(BaseModel):
    id: int
    name: str
    description: str
    icon: Optional[str] = None