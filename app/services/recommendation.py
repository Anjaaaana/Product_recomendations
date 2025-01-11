from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from typing import List, Dict, Optional
from app.models import models
import logging

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self):
        self.cache_timeout = 3600

    async def get_recommendations(
        self, 
        user_id: int, 
        db: Session, 
        limit: int = 5,
        category: Optional[str] = None
    ) -> List[Dict]:
        try:
            # First get relevant category IDs
            category_ids = []
            if category:
                # Get parent category
                parent_cat = db.query(models.Category).filter(
                    func.lower(models.Category.name) == category.lower()
                ).first()
                
                if parent_cat:
                    category_ids.append(parent_cat.category_id)
                    # Get child categories
                    child_cats = db.query(models.Category).filter(
                        models.Category.parent_category_id == parent_cat.category_id
                    ).all()
                    category_ids.extend([c.category_id for c in child_cats])

            # Build product query
            product_query = db.query(models.Product)
            
            if category_ids:
                product_query = product_query.filter(
                    models.Product.category_id.in_(category_ids)
                )

            # Get all matching products
            products = product_query.all()

            if not products:
                return []

            recommendations = []
            
            for product in products:
                # Get category info
                category_info = db.query(models.Category).filter(
                    models.Category.category_id == product.category_id
                ).first()

                # Get interaction stats in a separate query
                interaction_stats = db.query(
                    func.coalesce(func.avg(models.UserInteraction.rating), 0).label('avg_rating'),
                    func.count(models.UserInteraction.interaction_id).label('interaction_count')
                ).filter(
                    models.UserInteraction.product_id == product.product_id
                ).first()

                avg_rating = float(interaction_stats[0] if interaction_stats[0] else 0)
                interaction_count = int(interaction_stats[1] if interaction_stats[1] else 0)

                # Calculate recommendation score
                score = 0.5  # Base score
                score += min((avg_rating / 5.0) * 0.3, 0.3)  # Rating contribution (up to 0.3)
                score += min((interaction_count / 10) * 0.2, 0.2)  # Popularity contribution (up to 0.2)

                recommendations.append({
                    "product_id": product.product_id,
                    "name": product.name,
                    "description": product.description,
                    "price": float(product.price),
                    "category_id": product.category_id,
                    "category_name": category_info.name if category_info else None,
                    "image_url": product.image_url,
                    "similarity_score": round(score, 2),
                    "average_rating": round(avg_rating, 1),
                    "interaction_count": interaction_count
                })

            # Sort by score (descending) and name (ascending)
            recommendations.sort(key=lambda x: (-x['similarity_score'], x['name']))
            
            return recommendations[:limit]

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            print(f"Detailed error: {str(e)}")  # For debugging
            raise