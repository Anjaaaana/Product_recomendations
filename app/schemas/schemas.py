from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Product related schemas
class CategoryBase(BaseModel):
    name: str
    parent_category_id: Optional[int] = None

class CategoryResponse(CategoryBase):
    category_id: int

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category_id: int
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    product_id: int  # Changed from id to product_id to match database
    created_at: datetime
    feedback: Optional[List['FeedbackResponse']] = None
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True

# Feedback related schemas
class FeedbackBase(BaseModel):
    product_id: int
    rating: int = Field(..., ge=1, le=5)
    feedback_text: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    user_id: int

class FeedbackResponse(FeedbackBase):
    interaction_id: int  # Changed from id to interaction_id
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True

# Recommendation related schemas
class RecommendationResponse(BaseModel):
    product_id: int
    name: str
    description: Optional[str]
    price: float
    category_id: int
    similarity_score: float = Field(..., ge=0, le=1)
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

class RecommendationRequest(BaseModel):
    user_id: int
    limit: int = Field(default=5, ge=1, le=50)
    category: Optional[str] = None

# User Interaction Schema
class UserInteractionBase(BaseModel):
    user_id: int
    product_id: int
    rating: Optional[int] = Field(None, ge=1, le=5)
    view_count: int = 0
    purchase_count: int = 0

class UserInteractionCreate(UserInteractionBase):
    pass

class UserInteractionResponse(UserInteractionBase):
    interaction_id: int
    interaction_date: datetime

    class Config:
        from_attributes = True