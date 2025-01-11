from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from app.models import models
from app.services.recommendation import RecommendationService

async def update_product_embeddings(db: Session):
    recommendation_service = RecommendationService()
    products = db.query(models.Product).all()
    
    for product in products:
        product_text = f"{product.name} {product.description}"
        embedding = await recommendation_service.get_product_embedding(product_text)
        product.embedding = embedding.tolist()
    
    db.commit()

def schedule_embedding_updates():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_product_embeddings, 'interval', hours=24)
    scheduler.start()