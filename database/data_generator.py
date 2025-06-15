import random
import sqlite3
import sys
import os
from datetime import datetime, timedelta
from faker import Faker

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import (
    create_database, get_session, Restaurant, MenuItem, Customer, Order, OrderItem, Review, InventoryItem
)

class RestaurantDataGenerator:
    """
    Generate realistic sample data for the restaurant analytics platform
    """
    
    def __init__(self):
        self.session = get_session()
        
        # Sample data lists
        self.restaurant_names = [
            "The Golden Spoon", "Bella Vista", "Dragon Palace", "Mama's Kitchen",
            "Ocean Breeze", "The Rustic Table", "Spice Garden", "Urban Bistro",
            "Sunset Grill", "The Cozy Corner"
        ]
        
        self.locations = [
            "Downtown", "Westside", "Eastside", "Northside", "Southside",
            "City Center", "Riverside", "Hillside", "Beachfront", "Suburban Plaza"
        ]
        
        self.cuisine_types = [
            "Italian", "Chinese", "Mexican", "American", "Indian",
            "Japanese", "Mediterranean", "Thai", "French", "Korean"
        ]
        
        self.food_categories = [
            "Appetizers", "Main Course", "Desserts", "Beverages", "Salads", "Soups"
        ]
        
        self.payment_methods = ["cash", "card", "digital"]
        self.order_types = ["dine-in", "takeout", "delivery"]
        self.age_groups = ["18-25", "26-35", "36-45", "46-55", "55+"]
        
    def generate_restaurants(self, count=5):
        """
        Generate sample restaurants
        """
        restaurants = []
        for i in range(count):
            restaurant = Restaurant(
                name=self.restaurant_names[i],
                location=self.locations[i],
                cuisine_type=self.cuisine_types[i],
                capacity=random.randint(50, 200)
            )
            restaurants.append(restaurant)
            self.session.add(restaurant)
        
        self.session.commit()
        return restaurants
    
    def generate_menu_items(self, restaurants, items_per_restaurant=20):
        """
        Generate menu items for each restaurant
        """
        menu_items = []
        
        # Sample menu items by category
        sample_items = {
            "Appetizers": [
                ("Caesar Salad", "Fresh romaine lettuce with parmesan", 12.99),
                ("Chicken Wings", "Spicy buffalo wings with ranch", 14.99),
                ("Mozzarella Sticks", "Crispy fried mozzarella", 9.99),
                ("Bruschetta", "Toasted bread with tomato and basil", 8.99)
            ],
            "Main Course": [
                ("Grilled Salmon", "Atlantic salmon with herbs", 24.99),
                ("Beef Steak", "Prime ribeye steak", 32.99),
                ("Chicken Parmesan", "Breaded chicken with marinara", 19.99),
                ("Vegetable Pasta", "Fresh pasta with seasonal vegetables", 16.99),
                ("Fish Tacos", "Grilled fish with avocado", 15.99)
            ],
            "Desserts": [
                ("Chocolate Cake", "Rich chocolate layer cake", 7.99),
                ("Tiramisu", "Classic Italian dessert", 8.99),
                ("Ice Cream", "Vanilla, chocolate, or strawberry", 5.99)
            ],
            "Beverages": [
                ("Coffee", "Freshly brewed coffee", 3.99),
                ("Soft Drink", "Coca-Cola, Pepsi, Sprite", 2.99),
                ("Fresh Juice", "Orange, apple, or cranberry", 4.99)
            ]
        }
        
        for restaurant in restaurants:
            for category, items in sample_items.items():
                for name, description, base_price in items:
                    # Add some price variation based on restaurant
                    price_multiplier = random.uniform(0.8, 1.3)
                    price = round(base_price * price_multiplier, 2)
                    
                    menu_item = MenuItem(
                        restaurant_id=restaurant.id,
                        name=name,
                        category=category,
                        price=price,
                        description=description,
                        calories=random.randint(200, 800),
                        is_available=random.choice([1, 1, 1, 0])  # 75% available
                    )
                    menu_items.append(menu_item)
                    self.session.add(menu_item)
        
        self.session.commit()
        return menu_items
    
    def generate_customers(self, count=100):
        """
        Generate sample customers
        """
        fake = Faker()
        customers = []
        
        for _ in range(count):
            customer = Customer(
                name=fake.name(),
                email=fake.email(),
                phone=fake.phone_number(),
                age_group=random.choice(self.age_groups),
                preferred_cuisine=random.choice(self.cuisine_types),
                loyalty_points=random.randint(0, 1000),
                registration_date=fake.date_between(start_date='-2y', end_date='today')
            )
            customers.append(customer)
            self.session.add(customer)
        
        self.session.commit()
        return customers
    
    def generate_orders(self, restaurants, customers, menu_items, count=500):
        """
        Generate sample orders
        """
        orders = []
        
        for _ in range(count):
            restaurant = random.choice(restaurants)
            customer = random.choice(customers)
            
            # Generate order date within last 6 months
            order_date = datetime.now() - timedelta(days=random.randint(0, 180))
            
            order = Order(
                restaurant_id=restaurant.id,
                customer_id=customer.id,
                order_date=order_date,
                total_amount=0,  # Will be calculated after adding items
                order_type=random.choice(self.order_types),
                status="completed",
                payment_method=random.choice(self.payment_methods),
                table_number=random.randint(1, 20) if random.choice([True, False]) else None
            )
            
            self.session.add(order)
            self.session.flush()  # Get the order ID
            
            # Add order items
            restaurant_menu = [item for item in menu_items if item.restaurant_id == restaurant.id]
            num_items = random.randint(1, 5)
            total_amount = 0
            
            for _ in range(num_items):
                menu_item = random.choice(restaurant_menu)
                quantity = random.randint(1, 3)
                unit_price = menu_item.price
                total_price = unit_price * quantity
                
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=menu_item.id,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price
                )
                
                self.session.add(order_item)
                total_amount += total_price
            
            order.total_amount = round(total_amount, 2)
            orders.append(order)
        
        self.session.commit()
        return orders
    
    def generate_reviews(self, restaurants, customers, orders, count=200):
        """
        Generate sample reviews
        """
        reviews = []
        fake = Faker()
        
        # Sample review texts by rating
        review_templates = {
            5: [
                "Absolutely amazing! The food was incredible and service was perfect.",
                "Best restaurant experience I've had in years. Highly recommended!",
                "Outstanding food quality and excellent atmosphere. Will definitely return."
            ],
            4: [
                "Great food and good service. Really enjoyed our meal here.",
                "Very good restaurant with tasty dishes. Minor wait time but worth it.",
                "Solid choice for dining. Good quality food and friendly staff."
            ],
            3: [
                "Average experience. Food was okay but nothing special.",
                "Decent restaurant. Some dishes were better than others.",
                "It was fine. Not bad but not exceptional either."
            ],
            2: [
                "Disappointing experience. Food was below expectations.",
                "Service was slow and food was mediocre. Expected better.",
                "Not impressed. Several issues with our order."
            ],
            1: [
                "Terrible experience. Poor food quality and bad service.",
                "Would not recommend. Multiple problems with our visit.",
                "Very disappointing. Food was cold and service was awful."
            ]
        }
        
        for _ in range(count):
            order = random.choice(orders)
            restaurant_id = order.restaurant_id
            customer_id = order.customer_id
            
            # Generate ratings (skewed towards higher ratings)
            overall_rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0]
            
            review = Review(
                restaurant_id=restaurant_id,
                customer_id=customer_id,
                rating=overall_rating,
                review_text=random.choice(review_templates[overall_rating]),
                review_date=order.order_date + timedelta(days=random.randint(0, 7)),
                food_rating=max(1, overall_rating + random.randint(-1, 1)),
                service_rating=max(1, overall_rating + random.randint(-1, 1)),
                ambiance_rating=max(1, overall_rating + random.randint(-1, 1))
            )
            
            reviews.append(review)
            self.session.add(review)
        
        self.session.commit()
        return reviews
    
    def generate_all_data(self):
        """
        Generate all sample data for the platform
        """
        print("🏗️  Generating sample data for Restaurant Analytics Platform...")
        
        # Create database tables
        create_database()
        
        # Generate data in order
        print("📍 Generating restaurants...")
        restaurants = self.generate_restaurants(5)
        
        print("🍽️  Generating menu items...")
        menu_items = self.generate_menu_items(restaurants)
        
        print("👥 Generating customers...")
        customers = self.generate_customers(100)
        
        print("📦 Generating orders...")
        orders = self.generate_orders(restaurants, customers, menu_items, 500)
        
        print("⭐ Generating reviews...")
        reviews = self.generate_reviews(restaurants, customers, orders, 200)
        
        print(f"✅ Sample data generation complete!")
        print(f"   - {len(restaurants)} restaurants")
        print(f"   - {len(menu_items)} menu items")
        print(f"   - {len(customers)} customers")
        print(f"   - {len(orders)} orders")
        print(f"   - {len(reviews)} reviews")
        
        self.session.close()
        return {
            'restaurants': len(restaurants),
            'menu_items': len(menu_items),
            'customers': len(customers),
            'orders': len(orders),
            'reviews': len(reviews)
        }

if __name__ == "__main__":
    generator = RestaurantDataGenerator()
    generator.generate_all_data()