from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    interactions = relationship("UserInteraction", back_populates="user")
    feedback = relationship("UserFeedback", back_populates="user")

class Product(Base):
    __tablename__ = "products"
    
    product_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    image_url = Column(String(255))
    
    # Relationships
    category = relationship("Category", back_populates="products")
    interactions = relationship("UserInteraction", back_populates="product")
    feedback = relationship("UserFeedback", back_populates="product")

class Category(Base):
    __tablename__ = "categories"
    
    category_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    parent_category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True)
    
    # Relationships
    products = relationship("Product", back_populates="category")
    subcategories = relationship("Category", backref="parent", remote_side=[category_id])

class UserInteraction(Base):
    __tablename__ = "user_interactions"
    
    interaction_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    rating = Column(Integer)
    view_count = Column(Integer, default=0)
    purchase_count = Column(Integer, default=0)
    interaction_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="interactions")
    product = relationship("Product", back_populates="interactions")

class UserFeedback(Base):
    __tablename__ = "user_feedback"
    
    feedback_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    rating = Column(Integer)
    feedback_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="feedback")
    product = relationship("Product", back_populates="feedback")