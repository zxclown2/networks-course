from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from fastapi.responses import FileResponse
from server.core.schemas.product.product_api import (
    CreateRequest,
    CreateResponse,
    DeleteResponse,
    GetResponse,
    ListResponse,
    UpdateRequest,
    UpdateResponse,
)
from server.core.schemas.product.product_entity import Product
from server.core.storage.storage import get_storage

import random
import sys
import os

router = APIRouter(prefix="", tags=["product"])
storage_path = "products.json"

max_id = 10000000
def get_storage_instance():
    return get_storage(storage_path).get_data()

@router.post("/product", response_model=CreateResponse, status_code=status.HTTP_200_OK)
async def create_product(
    payload: CreateRequest,
    storage = Depends(get_storage_instance)
) -> CreateResponse:
    product_id = random.randint(0, max_id)
    while product_id in storage:
        product_id = random.randint(0, max_id)
    storage[product_id] = Product(
        id=product_id,
        name=payload.name,
        description=payload.description,
    )
    return storage[product_id]

@router.get("/product/{product_id}", response_model=GetResponse, status_code=status.HTTP_200_OK)
async def get_product(
    product_id: int,
    storage = Depends(get_storage_instance)
) -> GetResponse:
    if product_id not in storage:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"product with product_id {product_id} not found")
    return storage[product_id]

@router.delete("/product/{product_id}", response_model=DeleteResponse, status_code=status.HTTP_200_OK)
async def delete_product(
    product_id: int,
    storage = Depends(get_storage_instance)
) -> DeleteResponse:
    if product_id not in storage:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"product with product_id {product_id} not found")
    return storage.pop(product_id)

@router.put("/product/{product_id}", response_model=UpdateResponse, status_code=status.HTTP_200_OK)
async def update_product(
    product_id: int,
    payload: UpdateRequest,
    storage = Depends(get_storage_instance)
) -> CreateResponse:
    if product_id not in storage:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"product with product_id {product_id} not found")
    product = storage.pop(product_id).model_dump()
    for key, value in payload.model_dump().items():
        if value:
            product[key] = value
    result = Product(**product)
    storage[product["id"]] = result
    return result

@router.get("/products", response_model=ListResponse, status_code=status.HTTP_200_OK)
async def create_product(
    storage = Depends(get_storage_instance)
) -> ListResponse:
    return ListResponse([x for _, x in storage.items()])

@router.post("/product/{product_id}/image", status_code=status.HTTP_200_OK)
async def load_product_image(
    product_id: int,
    file: UploadFile,
    storage = Depends(get_storage_instance)
):
    if product_id not in storage:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"product with product_id {product_id} not found")
    with open(f"files/{file.filename}", "wb") as f:
        f.write(file.file.read())
    storage[product_id].icon = file.filename

@router.get("/product/{product_id}/image", status_code=status.HTTP_200_OK)
async def get_product_image(
    product_id: int,
    storage = Depends(get_storage_instance)
):
    if product_id not in storage:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"product with product_id {product_id} not found")
    if not storage[product_id].icon:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"product with product_id {product_id} has no icon")
    path = f"files/{storage[product_id].icon}"
    if not os.path.exists(path):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"can not find icon for product with product_id {product_id}")
    return FileResponse(
        path=path,
        filename=f"icon for product {product_id}",
        media_type="application/octet-stream"
    )

