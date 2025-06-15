#!/usr/bin/env python3
"""
Smart Restaurant Analytics Platform - Startup Script

This script provides an easy way to start the application with different modes:
- Dashboard only (Streamlit)
- API only (FastAPI)
- Both services
- Initialize database

Usage:
    python run.py --mode dashboard    # Start Streamlit dashboard only
    python run.py --mode api         # Start FastAPI server only
    python run.py --mode both        # Start both services
    python run.py --mode init        # Initialize database with sample data
"""

import argparse
import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import fastapi
        import uvicorn
        import pandas
        import plotly
        import google.generativeai
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("Please copy .env.example to .env and configure your API keys")
        return False
    
    # Check for Google AI API key
    with open(env_file, 'r') as f:
        content = f.read()
        if "GOOGLE_API_KEY=" not in content or "your_google_ai_api_key_here" in content:
            print("⚠️  Google AI API key not configured in .env file")
            print("Please set your Google AI API key in the .env file")
            return False
    
    print("✅ Environment configuration looks good")
    return True

def initialize_database():
    """Initialize database with sample data"""
    print("🔄 Initializing database with sample data...")
    try:
        from database.data_generator import RestaurantDataGenerator
        generator = RestaurantDataGenerator()
        stats = generator.generate_all_data()
        print("✅ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def start_streamlit():
    """Start Streamlit dashboard"""
    print("🚀 Starting Streamlit dashboard...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port=8501"])
    except KeyboardInterrupt:
        print("\n🛑 Streamlit dashboard stopped")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")

def start_fastapi():
    """Start FastAPI server"""
    print("🚀 Starting FastAPI server...")
    try:
        subprocess.run([sys.executable, "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])
    except KeyboardInterrupt:
        print("\n🛑 FastAPI server stopped")
    except Exception as e:
        print(f"❌ Error starting FastAPI: {e}")

def start_both_services():
    """Start both Streamlit and FastAPI services"""
    print("🚀 Starting both services...")
    print("📊 Streamlit Dashboard: http://localhost:8501")
    print("🔗 FastAPI Server: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop both services\n")
    
    # Start FastAPI in a separate thread
    fastapi_thread = threading.Thread(target=start_fastapi, daemon=True)
    fastapi_thread.start()
    
    # Give FastAPI time to start
    time.sleep(3)
    
    # Start Streamlit in main thread
    try:
        start_streamlit()
    except KeyboardInterrupt:
        print("\n🛑 Both services stopped")

def main():
    """Main function to handle command line arguments and start services"""
    parser = argparse.ArgumentParser(
        description="Smart Restaurant Analytics Platform Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --mode dashboard    # Start only Streamlit dashboard
  python run.py --mode api         # Start only FastAPI server
  python run.py --mode both        # Start both services
  python run.py --mode init        # Initialize database with sample data
  python run.py --check            # Check dependencies and configuration
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["dashboard", "api", "both", "init"],
        default="both",
        help="Mode to run the application (default: both)"
    )
    
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check dependencies and configuration without starting services"
    )
    
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Skip dependency and environment checks"
    )
    
    args = parser.parse_args()
    
    print("🍽️  Smart Restaurant Analytics Platform")
    print("=" * 50)
    
    # Check dependencies and environment unless skipped
    if not args.skip_checks:
        if not check_dependencies():
            sys.exit(1)
        
        if not check_env_file():
            sys.exit(1)
    
    # If only checking, exit here
    if args.check:
        print("✅ All checks passed! Ready to run the application.")
        return
    
    # Handle different modes
    if args.mode == "init":
        if initialize_database():
            print("\n🎉 Database initialization complete!")
            print("You can now run the application with: python run.py --mode both")
        else:
            sys.exit(1)
    
    elif args.mode == "dashboard":
        print("\n📊 Starting Streamlit Dashboard only...")
        print("🌐 Dashboard will be available at: http://localhost:8501")
        start_streamlit()
    
    elif args.mode == "api":
        print("\n🔗 Starting FastAPI Server only...")
        print("🌐 API will be available at: http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        start_fastapi()
    
    elif args.mode == "both":
        start_both_services()

if __name__ == "__main__":
    main()