from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_db, create_tables
from models.user import User
from app.schemas import UserCreate, UserUpdate, UserResponse, APIResponse

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

# Initialize database tables
create_tables()

@router.post("/", response_model=APIResponse)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        db_user = User(
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            company_name=user_data.company_name,
            industry_type=user_data.industry_type,
            reckon_user_id=user_data.reckon_user_id
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return APIResponse(
            success=True,
            message="User created successfully",
            data={"user_id": db_user.id, "email": db_user.email}
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

@router.get("/{user_id}", response_model=APIResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_data = UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            company_name=user.company_name,
            industry_type=user.industry_type,
            reckon_user_id=user.reckon_user_id,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
        return APIResponse(
            success=True,
            message="User retrieved successfully",
            data=user_data.dict()
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user: {str(e)}"
        )

@router.get("/", response_model=APIResponse)
async def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all users"""
    try:
        users = db.query(User).offset(skip).limit(limit).all()
        users_data = []
        
        for user in users:
            user_data = UserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                phone=user.phone,
                company_name=user.company_name,
                industry_type=user.industry_type,
                reckon_user_id=user.reckon_user_id,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            users_data.append(user_data.dict())
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(users_data)} users",
            data={"users": users_data, "count": len(users_data)}
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving users: {str(e)}"
        )

@router.put("/{user_id}", response_model=APIResponse)
async def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    """Update user by ID"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update user fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        return APIResponse(
            success=True,
            message="User updated successfully",
            data={"user_id": user.id}
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}"
        )

@router.delete("/{user_id}", response_model=APIResponse)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user by ID"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db.delete(user)
        db.commit()
        
        return APIResponse(
            success=True,
            message="User deleted successfully",
            data={"user_id": user_id}
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )