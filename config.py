import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """
    Configuration class for the Smart Restaurant Analytics Platform
    """
    
    # API Keys - Load from environment variables
    GOOGLE_API_KEY = os.getenv("GOOGLE_AI_API_KEY")
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///restaurant_analytics.db")
    
    # LLM Configuration
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-pro")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
    
    # Application Settings
    APP_NAME = "Smart Restaurant Analytics Platform"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # Streamlit Configuration
    PAGE_TITLE = os.getenv("PAGE_TITLE", "🍽️ Smart Restaurant Analytics")
    PAGE_ICON = os.getenv("PAGE_ICON", "🍽️")
    LAYOUT = os.getenv("LAYOUT", "wide")
    
    # Sample Data Configuration
    SAMPLE_DATA_SIZE = int(os.getenv("SAMPLE_DATA_SIZE", "1000"))
    DATE_RANGE_DAYS = int(os.getenv("DATE_RANGE_DAYS", "365"))
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "localhost")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
    
    @classmethod
    def validate_config(cls):
        """
        Validate that all required configuration is present
        """
        if not cls.GOOGLE_API_KEY:
            raise ValueError(
                "Google API key is required. Please set GOOGLE_AI_API_KEY in your .env file.\n"
                "Get your API key from: https://makersuite.google.com/app/apikey"
            )
        
        return True
    
    @classmethod
    def get_database_url(cls):
        """
        Get the complete database URL
        """
        return cls.DATABASE_URL
    
    @classmethod
    def is_development(cls):
        """
        Check if running in development mode
        """
        return cls.ENVIRONMENT == "development"
    
    @classmethod
    def is_debug(cls):
        """
        Check if debug mode is enabled
        """
        return cls.DEBUG

# Validate configuration on import
if __name__ != "__main__":
    try:
        Config.validate_config()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Please check your .env file and ensure all required variables are set.")
