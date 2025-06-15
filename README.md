# 🍽️ Restaurant Analytics LLM Dashboard

**Transform your restaurant data into actionable insights with AI-powered natural language queries**

A comprehensive end-to-end project showcasing the power of Large Language Models (LLMs) combined with SQL databases to create an intelligent restaurant analytics platform. Ask questions in plain English and get instant insights from your restaurant data!

## 🚀 Features

### 🤖 Natural Language to SQL
- **Intelligent Query Processing**: Convert natural language questions into optimized SQL queries using Google Gemini
- **Context-Aware Analysis**: Understands restaurant domain terminology and relationships
- **Query Validation**: Ensures generated SQL is safe and syntactically correct
- **Smart Suggestions**: Provides related questions to explore data further

### 📊 Interactive Dashboard
- **Real-time Metrics**: Key performance indicators updated in real-time
- **Visual Analytics**: Beautiful charts and graphs using Plotly
- **Multi-page Interface**: Organized navigation between different analysis views
- **Responsive Design**: Works seamlessly on desktop and mobile devices

### 🔍 Advanced Analytics
- **Revenue Trend Analysis**: Track daily, weekly, and monthly revenue patterns
- **Cuisine Performance**: Compare different cuisine types and their popularity
- **Customer Insights**: Analyze customer behavior and preferences
- **Menu Optimization**: Identify best-performing menu items
- **Rating Analysis**: Monitor customer satisfaction trends

### 🛠️ Technical Excellence
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Database Management**: SQLAlchemy ORM with SQLite for easy deployment
- **Data Generation**: Realistic sample data generator for testing
- **Error Handling**: Robust error handling and validation
- **Documentation**: Comprehensive API documentation with Swagger UI

## 🏗️ Technology Stack

### Backend
- **Python 3.8+**: Core programming language
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM)
- **SQLite**: Lightweight, serverless database
- **Google Gemini**: Advanced LLM for natural language processing
- **LangChain**: Framework for developing LLM applications

### Frontend
- **Streamlit**: Interactive web application framework
- **Plotly**: Interactive visualization library
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing library

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google AI API key (get it from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Zinga18018/restaurant-analytics-llm.git
   cd restaurant-analytics-llm
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Google AI API key
   ```

5. **Initialize the database**
   ```bash
   python database/data_generator.py
   ```

### Running the Application

#### Option 1: Streamlit Dashboard (Recommended)
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`

#### Option 2: FastAPI Backend
```bash
uvicorn api.main:app --reload
```
API documentation available at `http://localhost:8000/docs`

#### Option 3: Both (Separate terminals)
```bash
# Terminal 1: API Server
uvicorn api.main:app --reload --port 8000

# Terminal 2: Streamlit Dashboard
streamlit run app.py --server.port 8501
```

## 📱 Usage Examples

### Natural Language Queries
Ask questions in plain English:
- "What are the top 5 best-selling menu items this month?"
- "Show me the revenue trend for the last 30 days"
- "Which cuisine type has the highest average rating?"
- "What's the busiest day of the week?"
- "How many orders did we receive yesterday?"

### Dashboard Features
- **📈 Analytics Dashboard**: Overview of key metrics and trends
- **🔍 Natural Language Query**: Interactive query interface
- **📋 Sample Questions**: Pre-built queries to get started
- **🗄️ Database Explorer**: Browse raw data and schema

## 🏛️ Project Structure

```
restaurant-analytics-llm/
├── 📱 app.py                 # Streamlit dashboard application
├── ⚙️ config.py              # Configuration settings
├── 🚀 run.py                 # Application launcher
├── 🧪 demo.py                # Demo script
├── 📋 requirements.txt       # Python dependencies
├── 📄 .env.example          # Environment variables template
├── 🔧 api/
│   └── main.py              # FastAPI backend server
├── 🗄️ database/
│   ├── models.py            # SQLAlchemy database models
│   └── data_generator.py    # Sample data generation
├── 🧠 services/
│   └── llm_service.py       # LLM integration service
└── 🧪 tests/
    └── test_llm_service.py  # Unit tests
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file with the following variables:

```env
# Required: Google AI API Key
GOOGLE_AI_API_KEY=your_google_ai_api_key_here

# Optional: Database Configuration
DATABASE_URL=sqlite:///restaurant_analytics.db

# Optional: Application Settings
DEBUG=True
ENVIRONMENT=development
```

### Database Schema
The application uses the following main tables:
- **restaurants**: Restaurant information
- **menu_items**: Menu items with pricing and categories
- **orders**: Customer orders with timestamps
- **order_items**: Individual items within orders
- **customers**: Customer information
- **reviews**: Customer reviews and ratings

## 🎯 Key Features Showcase

### 🤖 AI-Powered Query Processing
- Converts natural language to SQL using Google Gemini
- Understands context and restaurant domain terminology
- Provides intelligent query suggestions
- Validates and optimizes generated SQL

### 📊 Interactive Visualizations
- Real-time revenue charts with Plotly
- Cuisine performance comparisons
- Customer rating distributions
- Order volume trends

### 🎨 Modern UI/UX
- Dark theme with gradient backgrounds
- Glass-morphism design elements
- Responsive layout for all devices
- Intuitive navigation and user flow

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini** for powerful natural language processing
- **Streamlit** for the amazing web app framework
- **FastAPI** for the high-performance API framework
- **Plotly** for beautiful interactive visualizations

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/Zinga18018/restaurant-analytics-llm/issues) page
2. Create a new issue with detailed information
3. Join our community discussions

---

**⭐ Star this repository if you find it helpful!**

Built with ❤️ for the restaurant industry and AI enthusiasts.