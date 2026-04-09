# Restaurant Analytics LLM

AI-powered restaurant analytics dashboard that converts natural language questions into SQL queries using Google Gemini and LangChain.

## Features

- **Natural language to SQL** -- Ask questions in plain English, get instant insights from your restaurant database
- **Interactive dashboard** -- Real-time metrics, revenue trends, and cuisine performance charts built with Plotly
- **Menu optimization** -- Identify top-performing items and track customer satisfaction trends
- **RESTful API** -- FastAPI backend with Swagger documentation
- **Realistic sample data** -- Built-in data generator for testing and demos

## Quick Start

```bash
git clone https://github.com/Zinga18018/restaurant-analytics-llm.git
cd restaurant-analytics-llm
pip install -r requirements.txt
```

Create a `.env` file with your API key:
```
GOOGLE_API_KEY=your_key_here
```

Run the app:
```bash
streamlit run app.py
```

## Architecture

```
restaurant-analytics-llm/
  app.py               # Streamlit dashboard
  api.py               # FastAPI backend
  database.py          # SQLAlchemy models and setup
  llm_engine.py        # Gemini + LangChain query engine
  data_generator.py    # Sample data creation
  requirements.txt
```

## Tech Stack

Python, Streamlit, FastAPI, LangChain, Google Gemini, SQLAlchemy, SQLite, Plotly

## License

MIT
