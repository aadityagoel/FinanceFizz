from fastapi import APIRouter, HTTPException, status, Depends
from models.user import UserCreate, UserLogin, UserResponse, Token
from database import users_collection
from utils.auth import get_password_hash, verify_password, create_access_token, create_refresh_token, verify_token
from utils.helpers import generate_id
from datetime import datetime

router = APIRouter()

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """Register a new user"""
    # Check if user already exists
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user_id = generate_id("user_")
    hashed_password = get_password_hash(user.password)
    
    user_doc = {
        "user_id": user_id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "password": hashed_password,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    users_collection.insert_one(user_doc)
    
    # Create tokens
    access_token = create_access_token(data={"sub": user_id, "email": user.email})
    refresh_token = create_refresh_token(data={"sub": user_id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login user"""
    user = users_collection.find_one({"email": credentials.email})
    
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user["user_id"], "email": user["email"]})
    refresh_token = create_refresh_token(data={"sub": user["user_id"]})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    payload = verify_token(refresh_token, "refresh")
    user_id = payload.get("sub")
    
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new tokens
    access_token = create_access_token(data={"sub": user_id, "email": user["email"]})
    new_refresh_token = create_refresh_token(data={"sub": user_id})
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(lambda: __import__('utils.dependencies', fromlist=['get_current_user']).get_current_user)):
    """Get current user information"""
    from utils.dependencies import get_current_user
    user = await get_current_user()
    
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user["role"],
        "created_at": user["created_at"]
    }