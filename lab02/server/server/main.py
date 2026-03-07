from fastapi import FastAPI

from server.api.routes.product import router as product_router
from server.core.storage.storage import get_storages

def get_application() -> FastAPI:
    app = FastAPI(title="test_server")
    app.include_router(product_router)
    return app

app = get_application()

@app.on_event("shutdown")
async def shutdown_storages():
    for path, storage in get_storages().items():
        storage.dump()