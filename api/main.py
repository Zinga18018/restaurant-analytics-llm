from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import pandas as pd
from services.llm_service import RestaurantAnalytics
from database.data_generator import RestaurantDataGenerator
from config import Config
import sqlite3
import json
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="Smart Restaurant Analytics API",
    description="AI-powered restaurant analytics platform with natural language to SQL conversion",
    version=Config.VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analytics service
analytics_service = RestaurantAnalytics()

# Pydantic models for request/response
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    sql_query: str
    results: List[Dict]
    insights: str
    related_questions: List[str]
    success: bool
    error: str = ""

class MetricsResponse(BaseModel):
    total_restaurants: int
    total_orders: int
    total_revenue: float
    average_rating: float
    total_customers: int
    last_updated: str

class RestaurantInfo(BaseModel):
    id: int
    name: str
    location: str
    cuisine_type: str
    capacity: int

class MenuItemInfo(BaseModel):
    id: int
    name: str
    category: str
    price: float
    description: str
    calories: int
    is_available: bool

# Dependency to get database connection
def get_db_connection():
    conn = sqlite3.connect("restaurant_analytics.db")
    try:
        yield conn
    finally:
        conn.close()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Smart Restaurant Analytics API",
        "version": Config.VERSION,
        "docs": "/docs",
        "endpoints": {
            "query": "/api/query",
            "metrics": "/api/metrics",
            "restaurants": "/api/restaurants",
            "sample-questions": "/api/sample-questions"
        }
    }

@app.post("/api/query", response_model=QueryResponse)
async def process_natural_language_query(request: QueryRequest):
    """
    Process a natural language question and return SQL query, results, and insights
    """
    try:
        sql_query, results, insights = analytics_service.process_natural_language_query(request.question)
        
        # Convert DataFrame to list of dictionaries
        if isinstance(results, pd.DataFrame):
            results_dict = results.to_dict('records')
        else:
            results_dict = []
        
        # Get related questions
        related_questions = analytics_service.get_related_questions(request.question, results)
        
        return QueryResponse(
            question=request.question,
            sql_query=sql_query,
            results=results_dict,
            insights=insights,
            related_questions=related_questions,
            success=True
        )
        
    except Exception as e:
        return QueryResponse(
            question=request.question,
            sql_query="",
            results=[],
            insights="",
            related_questions=[],
            success=False,
            error=str(e)
        )

@app.get("/api/metrics", response_model=MetricsResponse)
async def get_dashboard_metrics(conn: sqlite3.Connection = Depends(get_db_connection)):
    """
    Get key metrics for the dashboard
    """
    try:
        # Total restaurants
        total_restaurants = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM restaurants", conn
        ).iloc[0]['count']
        
        # Total orders
        total_orders = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM orders", conn
        ).iloc[0]['count']
        
        # Total revenue
        total_revenue = pd.read_sql_query(
            "SELECT COALESCE(SUM(total_amount), 0) as revenue FROM orders", conn
        ).iloc[0]['revenue']
        
        # Average rating
        average_rating = pd.read_sql_query(
            "SELECT COALESCE(AVG(rating), 0) as rating FROM reviews", conn
        ).iloc[0]['rating']
        
        # Total customers
        total_customers = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM customers", conn
        ).iloc[0]['count']
        
        return MetricsResponse(
            total_restaurants=total_restaurants,
            total_orders=total_orders,
            total_revenue=float(total_revenue),
            average_rating=float(average_rating),
            total_customers=total_customers,
            last_updated=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/restaurants", response_model=List[RestaurantInfo])
async def get_restaurants(conn: sqlite3.Connection = Depends(get_db_connection)):
    """
    Get list of all restaurants
    """
    try:
        restaurants_df = pd.read_sql_query(
            "SELECT id, name, location, cuisine_type, capacity FROM restaurants", conn
        )
        
        return [RestaurantInfo(**row) for row in restaurants_df.to_dict('records')]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/restaurants/{restaurant_id}/menu", response_model=List[MenuItemInfo])
async def get_restaurant_menu(restaurant_id: int, conn: sqlite3.Connection = Depends(get_db_connection)):
    """
    Get menu items for a specific restaurant
    """
    try:
        menu_df = pd.read_sql_query(
            """
            SELECT id, name, category, price, description, calories, is_available
            FROM menu_items 
            WHERE restaurant_id = ?
            ORDER BY category, name
            """, 
            conn, 
            params=[restaurant_id]
        )
        
        if menu_df.empty:
            raise HTTPException(status_code=404, detail="Restaurant not found or no menu items")
        
        return [MenuItemInfo(**row) for row in menu_df.to_dict('records')]
        
    except Exception as e:
        if "Restaurant not found" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sample-questions")
async def get_sample_questions():
    """
    Get sample questions for users to try
    """
    return {
        "questions": [
            "What are the top 5 best-selling menu items this month?",
            "Show me the revenue trend for the last 30 days",
            "Which cuisine type has the highest average rating?",
            "What's the busiest day of the week?",
            "How many orders did we receive yesterday?",
            "Which restaurant has the most loyal customers?",
            "What's the average order value by cuisine type?",
            "Show me customer reviews with ratings below 3",
            "Which menu items have the highest profit margins?",
            "What are the peak hours for orders?",
            "How does customer age group affect order preferences?",
            "Which payment method is most popular?",
            "Show me seasonal trends in our data",
            "What's the correlation between restaurant capacity and revenue?",
            "Which customers have the highest loyalty points?"
        ]
    }

@app.post("/api/initialize-data")
async def initialize_sample_data():
    """
    Initialize the database with sample data
    """
    try:
        generator = RestaurantDataGenerator()
        stats = generator.generate_all_data()
        
        return {
            "message": "Sample data generated successfully",
            "statistics": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating data: {str(e)}")

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint
    """
    try:
        # Test database connection
        conn = sqlite3.connect("restaurant_analytics.db")
        conn.execute("SELECT 1")
        conn.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected"
        }
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/api/database/tables")
async def get_database_schema(conn: sqlite3.Connection = Depends(get_db_connection)):
    """
    Get database schema information
    """
    try:
        # Get table names
        tables_df = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table'", conn
        )
        
        schema_info = {}
        
        for table_name in tables_df['name']:
            # Get column information for each table
            columns_df = pd.read_sql_query(
                f"PRAGMA table_info({table_name})", conn
            )
            
            # Get row count
            count_df = pd.read_sql_query(
                f"SELECT COUNT(*) as count FROM {table_name}", conn
            )
            
            schema_info[table_name] = {
                "columns": columns_df.to_dict('records'),
                "row_count": count_df.iloc[0]['count']
            }
        
        return schema_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)