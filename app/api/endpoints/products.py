from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import models
from app.schemas import schemas
from app.models.database import get_db
from app.services.recommendation import RecommendationService
from app.core.security import oauth2_scheme, verify_token
from sqlalchemy import or_, func

router = APIRouter()
recommendation_service = RecommendationService()

# Add this function to verify the current user
async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> models.User:
    email = verify_token(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/search", response_model=List[schemas.ProductResponse])
async def search_products(
    query: str = Query(..., description="Search term in product name or description"),
    category: Optional[str] = Query(None, description="Category name"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    sort_by: str = Query("relevance", description="Sorting criteria (relevance, price_asc, price_desc, rating)"),
    db: Session = Depends(get_db)
):
    """
    Search products with filtering and sorting capabilities.
    No authentication required.
    """
    try:
        products_query = db.query(models.Product)

        if query:
            products_query = products_query.filter(
                or_(
                    models.Product.name.ilike(f"%{query}%"),
                    models.Product.description.ilike(f"%{query}%")
                )
            )

        if category:
            products_query = products_query.join(
                models.Category,
                models.Product.category_id == models.Category.category_id
            ).filter(models.Category.name.ilike(f"%{category}%"))

        if min_price is not None:
            products_query = products_query.filter(models.Product.price >= min_price)
        if max_price is not None:
            products_query = products_query.filter(models.Product.price <= max_price)

        if sort_by == "price_asc":
            products_query = products_query.order_by(models.Product.price.asc())
        elif sort_by == "price_desc":
            products_query = products_query.order_by(models.Product.price.desc())
        elif sort_by == "rating":
            products_query = products_query.outerjoin(models.UserInteraction)\
                .group_by(models.Product.product_id)\
                .order_by(func.avg(models.UserInteraction.rating).desc())
            
        return products_query.all()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching products: {str(e)}"
        )

@router.get("/recommendations", response_model=List[schemas.RecommendationResponse])
async def get_recommendations(
    user_id: int = Query(..., description="User ID to get recommendations for"),
    limit: int = Query(5, description="Number of recommendations to return"),
    category: Optional[str] = Query(None, description="Filter recommendations by category"),
    db: Session = Depends(get_db)
):
    """
    Get personalized product recommendations for a user.
    No authentication required.
    """
    try:
        # Verify user exists
        user = db.query(models.User).filter(models.User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        recommendations = await recommendation_service.get_recommendations(
            user_id=user_id,
            db=db,
            limit=limit,
            category=category
        )
        return recommendations

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )
@router.post("/feedback", response_model=schemas.FeedbackResponse)
async def submit_feedback(
    feedback: schemas.FeedbackCreate,
    current_user: models.User = Depends(get_current_user),  # Changed this line
    db: Session = Depends(get_db)
):
    """
    Submit user feedback for a product.
    Requires authentication.
    """
    try:
        # Verify product exists
        product = db.query(models.Product).filter(
            models.Product.product_id == feedback.product_id
        ).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # Verify user exists
        user = db.query(models.User).filter(
            models.User.user_id == feedback.user_id
        ).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Verify rating is within valid range
        if feedback.rating < 1 or feedback.rating > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )

        db_feedback = models.UserFeedback(
            user_id=feedback.user_id,
            product_id=feedback.product_id,
            rating=feedback.rating,
            feedback_text=feedback.feedback_text
        )
        db.add(db_feedback)
        
        interaction = db.query(models.UserInteraction).filter(
            models.UserInteraction.user_id == feedback.user_id,
            models.UserInteraction.product_id == feedback.product_id
        ).first()
        
        if interaction:
            interaction.rating = feedback.rating
        else:
            new_interaction = models.UserInteraction(
                user_id=feedback.user_id,
                product_id=feedback.product_id,
                rating=feedback.rating,
                view_count=1
            )
            db.add(new_interaction)

        db.commit()
        db.refresh(db_feedback)
        return db_feedback

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting feedback: {str(e)}"
        )

@router.get("/{product_id}", response_model=schemas.ProductResponse)
async def get_product(
    product_id: int,
    current_user: models.User = Depends(get_current_user),  # Changed this line
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific product.
    Requires authentication.
    """
    try:
        product = db.query(models.Product).filter(
            models.Product.product_id == product_id
        ).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving product: {str(e)}"
        )