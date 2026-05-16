from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.schemas import UserRegister, UserLogin, TokenResponse, TokenRefresh
from app.services.user_service import UserService
from app.core.security import create_access_token, create_refresh_token, decode_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    existing = await UserService.get_by_username(db, data.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = await UserService.create_user(db, data)
    access = create_access_token({"sub": str(user.id)})
    refresh = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await UserService.authenticate(db, data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.is_banned:
        raise HTTPException(status_code=403, detail="Account banned")
    access = create_access_token({"sub": str(user.id)})
    refresh = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    payload = decode_token(data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user_id = payload.get("sub")
    user = await UserService.get_user(db, int(user_id))
    if not user or user.is_banned:
        raise HTTPException(status_code=401, detail="User not found")
    access = create_access_token({"sub": str(user.id)})
    refresh = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(access_token=access, refresh_token=refresh)
