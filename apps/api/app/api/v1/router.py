from fastapi import APIRouter, Depends

from app.api.v1.routes import (
    cars,
    chatbot,
    conversations,
    product_search,
    saved_cars,
    searches,
    vehicles,
)
from app.auth.dependencies import get_current_member

api_router = APIRouter(dependencies=[Depends(get_current_member)])
api_router.include_router(cars.router, prefix="/cars", tags=["cars"])
api_router.include_router(searches.router, prefix="/searches", tags=["searches"])
api_router.include_router(saved_cars.router, prefix="/saved-cars", tags=["saved cars"])
api_router.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])
api_router.include_router(product_search.router, prefix="/product-search", tags=["product search"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
api_router.include_router(vehicles.saved_router, prefix="/saved-vehicles", tags=["saved vehicles"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
