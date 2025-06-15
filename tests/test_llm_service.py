import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_service import LLMSQLService, RestaurantAnalytics

class TestLLMSQLService(unittest.TestCase):
    """Test cases for LLMSQLService class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock the Google Gemini API
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel'):
                self.service = LLMSQLService()
    
    def test_schema_info_generation(self):
        """Test that schema information is properly generated"""
        schema_info = self.service._get_schema_info()
        
        # Check that schema contains expected table information
        self.assertIn("restaurants", schema_info)
        self.assertIn("menu_items", schema_info)
        self.assertIn("customers", schema_info)
        self.assertIn("orders", schema_info)
        self.assertIn("order_items", schema_info)
        self.assertIn("reviews", schema_info)
    
    def test_sql_prompt_creation(self):
        """Test SQL prompt creation"""
        question = "What are the top 5 restaurants by revenue?"
        prompt = self.service._create_sql_prompt(question)
        
        # Check that prompt contains the question and schema
        self.assertIn(question, prompt)
        self.assertIn("restaurants", prompt)
        self.assertIn("SQL Query:", prompt)
    
    def test_sql_query_cleaning(self):
        """Test SQL query cleaning functionality"""
        # Test removing markdown code blocks
        sql_with_markdown = "```sql\nSELECT * FROM restaurants;\n```"
        cleaned = self.service._clean_sql_query(sql_with_markdown)
        self.assertEqual(cleaned, "SELECT * FROM restaurants;")
        
        # Test adding semicolon
        sql_without_semicolon = "SELECT * FROM restaurants"
        cleaned = self.service._clean_sql_query(sql_without_semicolon)
        self.assertEqual(cleaned, "SELECT * FROM restaurants;")
        
        # Test whitespace removal
        sql_with_whitespace = "  SELECT * FROM restaurants;  "
        cleaned = self.service._clean_sql_query(sql_with_whitespace)
        self.assertEqual(cleaned, "SELECT * FROM restaurants;")
    
    @patch('sqlite3.connect')
    def test_sql_execution(self, mock_connect):
        """Test SQL query execution"""
        # Mock database connection and results
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Mock pandas read_sql_query
        with patch('pandas.read_sql_query') as mock_read_sql:
            mock_df = pd.DataFrame({'name': ['Restaurant A'], 'revenue': [1000]})
            mock_read_sql.return_value = mock_df
            
            result = self.service.execute_sql("SELECT name, revenue FROM restaurants;")
            
            # Verify the result
            self.assertIsInstance(result, pd.DataFrame)
            self.assertEqual(len(result), 1)
            self.assertEqual(result.iloc[0]['name'], 'Restaurant A')
    
    def test_results_summary_preparation(self):
        """Test preparation of results summary for LLM analysis"""
        # Create sample DataFrame
        df = pd.DataFrame({
            'restaurant_name': ['Restaurant A', 'Restaurant B'],
            'revenue': [1000, 1500],
            'rating': [4.5, 4.2]
        })
        
        summary = self.service._prepare_results_summary(df)
        
        # Check that summary contains expected information
        self.assertIn("Number of rows: 2", summary)
        self.assertIn("restaurant_name, revenue, rating", summary)
        self.assertIn("Restaurant A", summary)
        self.assertIn("Numeric column statistics", summary)
    
    @patch('google.generativeai.GenerativeModel')
    def test_generate_sql(self, mock_model_class):
        """Test SQL generation from natural language"""
        # Mock the model and its response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "SELECT name, SUM(total_amount) as revenue FROM restaurants r JOIN orders o ON r.id = o.restaurant_id GROUP BY r.name ORDER BY revenue DESC LIMIT 5;"
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # Recreate service with mocked model
        with patch('google.generativeai.configure'):
            service = LLMSQLService()
            service.model = mock_model
        
        question = "What are the top 5 restaurants by revenue?"
        sql_query = service.generate_sql(question)
        
        # Verify SQL query generation
        self.assertIn("SELECT", sql_query)
        self.assertIn("restaurants", sql_query)
        self.assertIn("revenue", sql_query)
        self.assertTrue(sql_query.endswith(';'))
    
    @patch('google.generativeai.GenerativeModel')
    def test_generate_insights(self, mock_model_class):
        """Test insights generation from query results"""
        # Mock the model and its response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "The data shows that Restaurant A is the top performer with $1000 in revenue."
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # Recreate service with mocked model
        with patch('google.generativeai.configure'):
            service = LLMSQLService()
            service.model = mock_model
        
        # Create sample results
        results = pd.DataFrame({
            'restaurant_name': ['Restaurant A'],
            'revenue': [1000]
        })
        
        question = "What are the top restaurants by revenue?"
        insights = service.generate_insights(question, results)
        
        # Verify insights generation
        self.assertIn("Restaurant A", insights)
        self.assertIn("revenue", insights)
    
    def test_get_related_questions_fallback(self):
        """Test fallback related questions when API fails"""
        # Create sample results
        results = pd.DataFrame({'name': ['Restaurant A'], 'revenue': [1000]})
        
        # Mock API failure
        with patch.object(self.service, 'model') as mock_model:
            mock_model.generate_content.side_effect = Exception("API Error")
            
            questions = self.service.get_related_questions("test question", results)
            
            # Should return fallback questions
            self.assertIsInstance(questions, list)
            self.assertTrue(len(questions) > 0)
            self.assertIn("top-performing menu items", questions[0])

class TestRestaurantAnalytics(unittest.TestCase):
    """Test cases for RestaurantAnalytics class"""
    
    def setUp(self):
        """Set up test fixtures"""
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel'):
                self.analytics = RestaurantAnalytics()
    
    @patch.object(LLMSQLService, 'generate_sql')
    @patch.object(LLMSQLService, 'execute_sql')
    @patch.object(LLMSQLService, 'generate_insights')
    def test_process_natural_language_query(self, mock_insights, mock_execute, mock_generate):
        """Test complete natural language query processing"""
        # Mock the service methods
        mock_generate.return_value = "SELECT * FROM restaurants;"
        mock_execute.return_value = pd.DataFrame({'name': ['Restaurant A']})
        mock_insights.return_value = "This shows restaurant data."
        
        question = "Show me all restaurants"
        sql_query, results, insights = self.analytics.process_natural_language_query(question)
        
        # Verify the results
        self.assertEqual(sql_query, "SELECT * FROM restaurants;")
        self.assertIsInstance(results, pd.DataFrame)
        self.assertEqual(insights, "This shows restaurant data.")
        
        # Verify methods were called
        mock_generate.assert_called_once_with(question)
        mock_execute.assert_called_once_with("SELECT * FROM restaurants;")
        mock_insights.assert_called_once()
    
    def test_validate_query_safety(self):
        """Test SQL query safety validation"""
        # Safe queries
        safe_queries = [
            "SELECT * FROM restaurants;",
            "SELECT name, revenue FROM orders WHERE date > '2023-01-01';",
            "SELECT COUNT(*) FROM customers;"
        ]
        
        for query in safe_queries:
            self.assertTrue(self.analytics.validate_query_safety(query))
        
        # Dangerous queries
        dangerous_queries = [
            "DROP TABLE restaurants;",
            "DELETE FROM orders;",
            "UPDATE customers SET name = 'hacked';",
            "INSERT INTO restaurants VALUES (1, 'fake');",
            "ALTER TABLE customers ADD COLUMN hacked TEXT;",
            "CREATE TABLE malicious (id INT);"
        ]
        
        for query in dangerous_queries:
            self.assertFalse(self.analytics.validate_query_safety(query))

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow"""
    
    @patch('sqlite3.connect')
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_end_to_end_workflow(self, mock_model_class, mock_configure, mock_connect):
        """Test the complete end-to-end workflow"""
        # Mock database connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Mock model responses
        mock_model = Mock()
        mock_sql_response = Mock()
        mock_sql_response.text = "SELECT name, SUM(total_amount) as revenue FROM restaurants r JOIN orders o ON r.id = o.restaurant_id GROUP BY r.name;"
        
        mock_insights_response = Mock()
        mock_insights_response.text = "Restaurant A leads in revenue generation."
        
        mock_questions_response = Mock()
        mock_questions_response.text = "What are the peak hours?\nWhich cuisine is most popular?\nHow do ratings correlate with revenue?"
        
        # Configure mock to return different responses based on prompt content
        def mock_generate_content(prompt):
            if "SQL Query:" in prompt:
                return mock_sql_response
            elif "provide actionable insights" in prompt:
                return mock_insights_response
            elif "suggest 5 related questions" in prompt:
                return mock_questions_response
            else:
                return mock_sql_response
        
        mock_model.generate_content.side_effect = mock_generate_content
        mock_model_class.return_value = mock_model
        
        # Mock pandas read_sql_query
        with patch('pandas.read_sql_query') as mock_read_sql:
            mock_df = pd.DataFrame({
                'name': ['Restaurant A', 'Restaurant B'],
                'revenue': [1500, 1200]
            })
            mock_read_sql.return_value = mock_df
            
            # Create analytics service and process query
            analytics = RestaurantAnalytics()
            question = "What are the top restaurants by revenue?"
            
            sql_query, results, insights = analytics.process_natural_language_query(question)
            related_questions = analytics.get_related_questions(question, results)
            
            # Verify results
            self.assertIn("SELECT", sql_query)
            self.assertIsInstance(results, pd.DataFrame)
            self.assertEqual(len(results), 2)
            self.assertIn("Restaurant A", insights)
            self.assertIsInstance(related_questions, list)
            self.assertTrue(len(related_questions) > 0)

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)