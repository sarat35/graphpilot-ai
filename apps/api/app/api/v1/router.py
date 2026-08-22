from fastapi import APIRouter

from app.api.v1.routes import cars, chatbot, saved_cars, searches

api_router = APIRouter()
api_router.include_router(cars.router, prefix="/cars", tags=["cars"])
api_router.include_router(searches.router, prefix="/searches", tags=["searches"])
api_router.include_router(saved_cars.router, prefix="/saved-cars", tags=["saved cars"])
api_router.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])
