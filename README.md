# LLM-Based Product Recommendation System

A sophisticated product recommendation engine built with FastAPI and SQLAlchemy, enhanced with large language model capabilities for personalized product suggestions.

## 🌟 Features

- **Personalized Recommendations**: Leverages user interactions and preferences to suggest relevant products
- **LLM Integration**: Uses embeddings to understand product descriptions and user preferences
- **Category Filtering**: Filter recommendations by product categories and subcategories
- **Rating-Based Sorting**: Incorporates user ratings into recommendation algorithms
- **Performance Optimized**: Implements caching for faster response times

## 🏗️ Project Structure

```
app/
├── api/
│   └── endpoints/
│       ├── auth.py
│       └── products.py
├── core/
│   ├── security.py
│   └── cache.py
├── models/
│   ├── database.py
│   └── models.py
├── schemas/
│   └── schemas.py
├── services/
│   └── recommendation.py
└── main.py
```

## 🗄️ Database Models

### User
- Stores user authentication and profile information
- Linked to user interactions and feedback

### Product
- Contains product details including name, description, price
- Associated with categories and user interactions

### Category
- Hierarchical category structure with parent-child relationships
- Organizes products into browsable categories

### UserInteraction
- Tracks user engagement with products
- Records views, purchases, and ratings

### UserFeedback
- Collects detailed user feedback on products
- Includes ratings and text reviews

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- MySQL database
- Virtual environment (recommended)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/product-recommendation.git
   cd product-recommendation
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure database:
   - Update the database URL in `app/models/database.py`
   - Current config: `mysql+pymysql://Anjana:test123@localhost:3306/recommendation_system`

5. Initialize the database:
   ```bash
   python -m app.scripts.init_db
   ```

6. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## 🔧 Core Components

### Recommendation Service
The heart of the system, located in `app/services/recommendation.py`:
- Generates personalized product recommendations
- Calculates similarity scores based on user interactions
- Filters by category when requested
- Incorporates product ratings and popularity metrics

### Embedding Updates
Scheduled task that updates product embeddings daily:
- Extracts meaningful vectors from product descriptions
- Enables semantic similarity between products
- Improves recommendation quality over time

## 📊 Key Algorithms

### Recommendation Score Calculation
```python
score = 0.5  # Base score
score += min((avg_rating / 5.0) * 0.3, 0.3)  # Rating contribution (up to 0.3)
score += min((interaction_count / 10) * 0.2, 0.2)  # Popularity contribution (up to 0.2)
```

## 🛡️ Security

- Password hashing for user authentication
- Database session management
- API endpoint protection

## 🔄 Scheduled Tasks

The system includes scheduled tasks for:
- Updating product embeddings (daily)
- Can be configured in the scheduler module

## 📝 API Endpoints

### Authentication
- `POST /api/auth/register`: Register a new user
- `POST /api/auth/login`: Authenticate and get access token

### Products
- `GET /api/products/`: List all products
- `GET /api/products/{product_id}`: Get product details
- `GET /api/products/recommendations`: Get personalized recommendations

## 📚 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
