import google.generativeai as genai
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
import sqlite3
import pandas as pd
from typing import Dict, List, Tuple, Optional
import re
from config import Config

class LLMSQLService:
    """
    Service for converting natural language queries to SQL using Google Gemini
    """
    
    def __init__(self):
        # Configure Google Gemini
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Database connection
        self.db_path = "restaurant_analytics.db"
        
        # Schema information for context
        self.schema_info = self._get_schema_info()
        
    def _get_schema_info(self) -> str:
        """
        Get database schema information for context
        """
        schema_description = """
        DATABASE SCHEMA:
        
        1. restaurants: Restaurant information
           - id (INTEGER): Primary key
           - name (TEXT): Restaurant name
           - location (TEXT): Restaurant location
           - cuisine_type (TEXT): Type of cuisine (Italian, Chinese, etc.)
           - capacity (INTEGER): Seating capacity
           - created_at (DATETIME): Creation timestamp
        
        2. menu_items: Menu items for each restaurant
           - id (INTEGER): Primary key
           - restaurant_id (INTEGER): Foreign key to restaurants
           - name (TEXT): Item name
           - category (TEXT): Food category (Appetizers, Main Course, etc.)
           - price (REAL): Item price
           - description (TEXT): Item description
           - calories (INTEGER): Calorie count
           - is_available (INTEGER): 1 if available, 0 if not
        
        3. customers: Customer information
           - id (INTEGER): Primary key
           - name (TEXT): Customer name
           - email (TEXT): Customer email
           - age_group (TEXT): Age range (18-25, 26-35, etc.)
           - preferred_cuisine (TEXT): Preferred cuisine type
           - loyalty_points (INTEGER): Loyalty program points
           - registration_date (DATETIME): Registration date
        
        4. orders: Customer orders
           - id (INTEGER): Primary key
           - restaurant_id (INTEGER): Foreign key to restaurants
           - customer_id (INTEGER): Foreign key to customers
           - order_date (DATETIME): Order timestamp
           - total_amount (REAL): Total order value
           - order_type (TEXT): dine-in, takeout, or delivery
           - status (TEXT): Order status
           - payment_method (TEXT): cash, card, or digital
           - table_number (INTEGER): Table number if dine-in
        
        5. order_items: Items in each order
           - id (INTEGER): Primary key
           - order_id (INTEGER): Foreign key to orders
           - menu_item_id (INTEGER): Foreign key to menu_items
           - quantity (INTEGER): Number of items
           - unit_price (REAL): Price per unit
           - total_price (REAL): Total price for this item
        
        6. reviews: Customer reviews
           - id (INTEGER): Primary key
           - restaurant_id (INTEGER): Foreign key to restaurants
           - customer_id (INTEGER): Foreign key to customers
           - rating (INTEGER): Overall rating (1-5)
           - review_text (TEXT): Review content
           - review_date (DATETIME): Review timestamp
           - food_rating (INTEGER): Food rating (1-5)
           - service_rating (INTEGER): Service rating (1-5)
           - ambiance_rating (INTEGER): Ambiance rating (1-5)
        """
        return schema_description
    
    def _create_sql_prompt(self, question: str) -> str:
        """
        Create a prompt for SQL generation
        """
        prompt = f"""
        You are an expert SQL analyst for a restaurant analytics platform. Convert the following natural language question into a SQL query.
        
        {self.schema_info}
        
        IMPORTANT RULES:
        1. Generate ONLY valid SQLite syntax
        2. Use proper JOINs when accessing multiple tables
        3. Include appropriate WHERE clauses for filtering
        4. Use aggregate functions (COUNT, SUM, AVG) when appropriate
        5. Limit results to reasonable numbers (use LIMIT clause)
        6. Use proper date functions for time-based queries
        7. Return only the SQL query, no explanations
        
        Question: {question}
        
        SQL Query:
        """
        return prompt
    
    def generate_sql(self, question: str) -> str:
        """
        Generate SQL query from natural language question
        """
        try:
            prompt = self._create_sql_prompt(question)
            response = self.model.generate_content(prompt)
            
            # Extract SQL from response
            sql_query = response.text.strip()
            
            # Clean up the SQL query
            sql_query = self._clean_sql_query(sql_query)
            
            return sql_query
            
        except Exception as e:
            raise Exception(f"Error generating SQL: {str(e)}")
    
    def _clean_sql_query(self, sql_query: str) -> str:
        """
        Clean and validate the generated SQL query
        """
        # Remove markdown code blocks if present
        sql_query = re.sub(r'```sql\n?', '', sql_query)
        sql_query = re.sub(r'```\n?', '', sql_query)
        
        # Remove extra whitespace
        sql_query = sql_query.strip()
        
        # Ensure query ends with semicolon
        if not sql_query.endswith(';'):
            sql_query += ';'
        
        return sql_query
    
    def execute_sql(self, sql_query: str) -> pd.DataFrame:
        """
        Execute SQL query and return results as DataFrame
        """
        try:
            conn = sqlite3.connect(self.db_path)
            results = pd.read_sql_query(sql_query, conn)
            conn.close()
            return results
        except Exception as e:
            raise Exception(f"Error executing SQL: {str(e)}")
    
    def generate_insights(self, question: str, results: pd.DataFrame) -> str:
        """
        Generate insights from query results using LLM
        """
        try:
            if results.empty:
                return "No data found for the given query."
            
            # Prepare results summary for LLM
            results_summary = self._prepare_results_summary(results)
            
            prompt = f"""
            You are a restaurant business analyst. Based on the following query and results, provide actionable insights.
            
            Original Question: {question}
            
            Query Results Summary:
            {results_summary}
            
            Please provide:
            1. Key findings from the data
            2. Business implications
            3. Actionable recommendations
            
            Keep the response concise and business-focused.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            return f"Error generating insights: {str(e)}"
    
    def _prepare_results_summary(self, results: pd.DataFrame) -> str:
        """
        Prepare a summary of results for LLM analysis
        """
        summary = f"Number of rows: {len(results)}\n"
        summary += f"Columns: {', '.join(results.columns)}\n\n"
        
        # Add first few rows
        summary += "Sample data:\n"
        summary += results.head().to_string(index=False)
        
        # Add basic statistics for numeric columns
        numeric_cols = results.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary += "\n\nNumeric column statistics:\n"
            summary += results[numeric_cols].describe().to_string()
        
        return summary
    
    def get_related_questions(self, original_question: str, results: pd.DataFrame) -> List[str]:
        """
        Generate related questions based on the original query and results
        """
        try:
            prompt = f"""
            Based on the following restaurant analytics question and its results, suggest 5 related questions that would provide additional insights.
            
            Original Question: {original_question}
            
            Results columns: {', '.join(results.columns) if not results.empty else 'No results'}
            
            Generate questions that:
            1. Explore different aspects of the same topic
            2. Drill down into specific details
            3. Compare different time periods or segments
            4. Identify trends or patterns
            5. Focus on actionable business decisions
            
            Return only the questions, one per line, without numbering.
            """
            
            response = self.model.generate_content(prompt)
            questions = [q.strip() for q in response.text.strip().split('\n') if q.strip()]
            
            # Return up to 5 questions
            return questions[:5]
            
        except Exception as e:
            # Fallback to predefined related questions
            return [
                "What are the top-performing menu items by revenue?",
                "How do customer ratings vary by cuisine type?",
                "What are the peak ordering hours?",
                "Which restaurants have the highest customer retention?",
                "What's the average order value by customer age group?"
            ]

class RestaurantAnalytics:
    """
    Main analytics service that combines SQL generation with business insights
    """
    
    def __init__(self):
        self.llm_service = LLMSQLService()
    
    def process_natural_language_query(self, question: str) -> Tuple[str, pd.DataFrame, str]:
        """
        Process a natural language question and return SQL, results, and insights
        """
        # Generate SQL query
        sql_query = self.llm_service.generate_sql(question)
        
        # Execute query
        results = self.llm_service.execute_sql(sql_query)
        
        # Generate insights
        insights = self.llm_service.generate_insights(question, results)
        
        return sql_query, results, insights
    
    def get_related_questions(self, question: str, results: pd.DataFrame) -> List[str]:
        """
        Get related questions for further exploration
        """
        return self.llm_service.get_related_questions(question, results)
    
    def validate_query_safety(self, sql_query: str) -> bool:
        """
        Basic validation to ensure query safety
        """
        # Convert to lowercase for checking
        query_lower = sql_query.lower()
        
        # Check for dangerous operations
        dangerous_keywords = ['drop', 'delete', 'update', 'insert', 'alter', 'create']
        
        for keyword in dangerous_keywords:
            if keyword in query_lower:
                return False
        
        return True