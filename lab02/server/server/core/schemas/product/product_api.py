from pydantic import BaseModel, Field, RootModel
from server.core.schemas.product.product_entity import Product
from typing import List, Optional

DefaultResponse = Product

GetResponse = DefaultResponse
CreateResponse = DefaultResponse
UpdateResponse = DefaultResponse
DeleteResponse = DefaultResponse

class CreateRequest(BaseModel):
    name: str
    description: str


class UpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ListResponse(RootModel):
    root: List[Product]

