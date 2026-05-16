from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, marketplace, transactions, admin, support, bot_api

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(marketplace.router)
api_router.include_router(transactions.router)
api_router.include_router(admin.router)
api_router.include_router(support.router)
api_router.include_router(bot_api.router)
