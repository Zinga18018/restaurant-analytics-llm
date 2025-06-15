from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class Restaurant(Base):
    """
    Restaurant information table
    """
    __tablename__ = "restaurants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(200), nullable=False)
    cuisine_type = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = relationship("Order", back_populates="restaurant")
    menu_items = relationship("MenuItem", back_populates="restaurant")
    reviews = relationship("Review", back_populates="restaurant")

class MenuItem(Base):
    """
    Menu items table
    """
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text)
    ingredients = Column(Text)
    calories = Column(Integer)
    is_available = Column(Integer, default=1)  # 1 for available, 0 for unavailable
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="menu_items")
    order_items = relationship("OrderItem", back_populates="menu_item")

class Customer(Base):
    """
    Customer information table
    """
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    age_group = Column(String(20))  # 18-25, 26-35, 36-45, 46-55, 55+
    preferred_cuisine = Column(String(50))
    loyalty_points = Column(Integer, default=0)
    registration_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = relationship("Order", back_populates="customer")
    reviews = relationship("Review", back_populates="customer")

class Order(Base):
    """
    Orders table
    """
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    order_date = Column(DateTime, nullable=False)
    total_amount = Column(Float, nullable=False)
    order_type = Column(String(20), nullable=False)  # dine-in, takeout, delivery
    status = Column(String(20), default="completed")  # pending, preparing, completed, cancelled
    payment_method = Column(String(20))  # cash, card, digital
    table_number = Column(Integer)
    special_requests = Column(Text)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="orders")
    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    """
    Order items table (junction table for orders and menu items)
    """
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")

class Review(Base):
    """
    Customer reviews table
    """
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 scale
    review_text = Column(Text)
    review_date = Column(DateTime, default=datetime.utcnow)
    food_rating = Column(Integer)  # 1-5 scale
    service_rating = Column(Integer)  # 1-5 scale
    ambiance_rating = Column(Integer)  # 1-5 scale
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="reviews")
    customer = relationship("Customer", back_populates="reviews")

class InventoryItem(Base):
    """
    Inventory management table
    """
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    item_name = Column(String(100), nullable=False)
    category = Column(String(50))  # ingredients, beverages, supplies
    quantity = Column(Float, nullable=False)
    unit = Column(String(20))  # kg, liters, pieces, etc.
    cost_per_unit = Column(Float)
    supplier = Column(String(100))
    last_restocked = Column(DateTime)
    minimum_threshold = Column(Float)  # Reorder level
    
    # Relationships
    restaurant = relationship("Restaurant")

# Database setup functions
def create_database(database_url: str = "sqlite:///restaurant_analytics.db"):
    """
    Create database and all tables
    """
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    return engine

def get_session(database_url: str = "sqlite:///restaurant_analytics.db"):
    """
    Get database session
    """
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def init_database():
    """
    Initialize database with tables
    """
    if not os.path.exists("restaurant_analytics.db"):
        engine = create_database()
        print("✅ Database created successfully!")
        return engine
    else:
        print("📁 Database already exists.")
        return create_engine("sqlite:///restaurant_analytics.db")

if __name__ == "__main__":
    # Create database when run directly
    init_database()