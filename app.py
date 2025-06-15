import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
from services.llm_service import RestaurantAnalytics
from database.data_generator import RestaurantDataGenerator
from config import Config
import os

# Page configuration
st.set_page_config(
    page_title=Config.PAGE_TITLE,
    page_icon=Config.PAGE_ICON,
    layout=Config.LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Dark theme for main app */
    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: #ffffff;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
    
    /* Main content area */
    .main .block-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 2rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .insight-box {
        background: linear-gradient(135deg, rgba(78, 205, 196, 0.1) 0%, rgba(69, 183, 209, 0.1) 100%);
        border-left: 4px solid #4ECDC4;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 10px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(78, 205, 196, 0.2);
        color: #ffffff;
    }
    
    .sql-box {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        color: #e2e8f0;
        padding: 1.5rem;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }
    
    /* Chart containers */
    .stPlotlyChart {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Related questions styling */
    .related-questions {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .question-button {
        background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin: 0.25rem;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.9rem;
    }
    
    .question-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(78, 205, 196, 0.3);
    }
</style>
""", unsafe_allow_html=True)

def initialize_database():
    """Initialize database with sample data if it doesn't exist"""
    if not os.path.exists("restaurant_analytics.db"):
        st.info("🔄 Initializing database with sample data...")
        generator = RestaurantDataGenerator()
        generator.generate_all_data()
        st.success("✅ Database initialized successfully!")

def get_dashboard_metrics():
    """Get key metrics for the dashboard"""
    conn = sqlite3.connect("restaurant_analytics.db")
    
    # Total revenue
    total_revenue = pd.read_sql_query(
        "SELECT SUM(total_amount) as revenue FROM orders", conn
    ).iloc[0]['revenue'] or 0
    
    # Total orders
    total_orders = pd.read_sql_query(
        "SELECT COUNT(*) as orders FROM orders", conn
    ).iloc[0]['orders']
    
    # Average rating
    avg_rating = pd.read_sql_query(
        "SELECT AVG(rating) as rating FROM reviews", conn
    ).iloc[0]['rating'] or 0
    
    # Active customers
    active_customers = pd.read_sql_query(
        "SELECT COUNT(DISTINCT customer_id) as customers FROM orders", conn
    ).iloc[0]['customers']
    
    conn.close()
    return total_revenue, total_orders, avg_rating, active_customers

def create_revenue_chart():
    """Create revenue trend chart"""
    conn = sqlite3.connect("restaurant_analytics.db")
    
    query = """
    SELECT DATE(order_date) as date, SUM(total_amount) as revenue
    FROM orders
    GROUP BY DATE(order_date)
    ORDER BY date
    LIMIT 30
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        return None
    
    fig = px.line(
        df, x='date', y='revenue',
        title='📈 Daily Revenue Trend (Last 30 Days)',
        labels={'revenue': 'Revenue ($)', 'date': 'Date'}
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_size=20
    )
    
    fig.update_traces(
        line=dict(color='#4ECDC4', width=3),
        fill='tonexty',
        fillcolor='rgba(78, 205, 196, 0.1)'
    )
    
    return fig

def create_cuisine_chart():
    """Create cuisine performance chart"""
    conn = sqlite3.connect("restaurant_analytics.db")
    
    query = """
    SELECT r.cuisine_type, COUNT(o.id) as order_count, SUM(o.total_amount) as revenue
    FROM restaurants r
    JOIN orders o ON r.id = o.restaurant_id
    GROUP BY r.cuisine_type
    ORDER BY revenue DESC
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        return None
    
    fig = px.bar(
        df, x='cuisine_type', y='revenue',
        title='🍽️ Revenue by Cuisine Type',
        labels={'revenue': 'Revenue ($)', 'cuisine_type': 'Cuisine Type'},
        color='revenue',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_size=20
    )
    
    return fig

def main():
    """Main application function"""
    # Initialize session state for page navigation
    if 'page' not in st.session_state:
        st.session_state.page = "Analytics Dashboard"
    
    # Check if page should be changed from session state
    if 'selected_question' in st.session_state and st.session_state.selected_question:
        st.session_state.page = "Natural Language Query"
    
    # Header
    st.markdown('<h1 class="main-header">🍽️ Smart Restaurant Analytics</h1>', unsafe_allow_html=True)
    st.markdown("### Transform your restaurant data into actionable insights with AI-powered queries")
    
    # Initialize database
    initialize_database()
    
    # Initialize analytics service
    analytics = RestaurantAnalytics()
    
    # Sidebar navigation
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Analytics Dashboard", "Natural Language Query", "Sample Questions", "Database Explorer"],
        index=["Analytics Dashboard", "Natural Language Query", "Sample Questions", "Database Explorer"].index(st.session_state.page)
    )
    
    # Update session state if selectbox changed
    if page != st.session_state.page:
        st.session_state.page = page
    
    # Route to appropriate page
    if st.session_state.page == "Analytics Dashboard":
        show_dashboard()
    elif st.session_state.page == "Natural Language Query":
        show_query_interface(analytics)
    elif st.session_state.page == "Sample Questions":
        show_sample_questions()
    elif st.session_state.page == "Database Explorer":
        show_database_explorer()

def show_dashboard():
    """Show the main analytics dashboard"""
    st.header("📈 Restaurant Analytics Dashboard")
    
    # Get metrics
    total_revenue, total_orders, avg_rating, active_customers = get_dashboard_metrics()
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f'<div class="metric-card"><h3>💰 Total Revenue</h3><h2>${total_revenue:,.2f}</h2></div>',
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f'<div class="metric-card"><h3>📦 Total Orders</h3><h2>{total_orders:,}</h2></div>',
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f'<div class="metric-card"><h3>⭐ Avg Rating</h3><h2>{avg_rating:.1f}/5</h2></div>',
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f'<div class="metric-card"><h3>👥 Active Customers</h3><h2>{active_customers:,}</h2></div>',
            unsafe_allow_html=True
        )
    
    # Charts
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        revenue_chart = create_revenue_chart()
        if revenue_chart:
            st.plotly_chart(revenue_chart, use_container_width=True)
    
    with col2:
        cuisine_chart = create_cuisine_chart()
        if cuisine_chart:
            st.plotly_chart(cuisine_chart, use_container_width=True)

def show_query_interface(analytics):
    """Show the natural language query interface"""
    st.header("🤖 Natural Language Query Interface")
    st.markdown("Ask questions about your restaurant data in plain English!")
    
    # Get pre-filled question from session state
    default_query = ""
    if 'query_input' in st.session_state and st.session_state.query_input:
        default_query = st.session_state.query_input
        st.session_state.query_input = ""  # Clear after use
    elif 'selected_question' in st.session_state and st.session_state.selected_question:
        default_query = st.session_state.selected_question
        st.session_state.selected_question = ""  # Clear after use
    
    # Query input
    user_query = st.text_input(
        "Enter your question:",
        value=default_query,
        placeholder="e.g., What are the top 5 best-selling menu items this month?"
    )
    
    if st.button("🔍 Analyze", type="primary"):
        if user_query:
            with st.spinner("🤖 Processing your query..."):
                try:
                    # Generate SQL and get results
                    sql_query, results, insights = analytics.process_natural_language_query(user_query)
                    
                    # Display SQL query
                    st.subheader("🔧 Generated SQL Query")
                    st.markdown(f'<div class="sql-box">{sql_query}</div>', unsafe_allow_html=True)
                    
                    # Display results
                    st.subheader("📊 Query Results")
                    if isinstance(results, pd.DataFrame) and not results.empty:
                        st.dataframe(results, use_container_width=True)
                        
                        # Simple visualization heuristic
                        if len(results.columns) >= 2:
                            numeric_cols = results.select_dtypes(include=['number']).columns
                            if len(numeric_cols) >= 1:
                                fig = px.bar(
                                    results.head(10), 
                                    x=results.columns[0], 
                                    y=numeric_cols[0],
                                    title=f"📈 {user_query}"
                                )
                                fig.update_layout(
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    font_color='white'
                                )
                                st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No results found for your query.")
                    
                    # Display AI insights
                    if insights:
                        st.subheader("🧠 AI-Generated Insights")
                        st.markdown(f'<div class="insight-box">{insights}</div>', unsafe_allow_html=True)
                    
                    # Related questions
                    st.subheader("🔗 Related Questions")
                    related_questions = analytics.get_related_questions(user_query, results)
                    
                    if related_questions:
                        st.markdown('<div class="related-questions">', unsafe_allow_html=True)
                        for i, question in enumerate(related_questions):
                            if st.button(f"📝 {question}", key=f"related_{i}"):
                                st.session_state.query_input = question
                                st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ Error processing query: {str(e)}")
                    st.info("💡 Try rephrasing your question or check if the data exists in the database.")
        else:
            st.warning("⚠️ Please enter a question to analyze.")

def show_sample_questions():
    """Show sample questions to get users started"""
    st.header("📋 Sample Questions")
    st.markdown("Get started with these example questions:")
    
    sample_questions = [
        "What are the top 5 best-selling menu items this month?",
        "Show me the revenue trend for the last 30 days",
        "Which cuisine type has the highest average rating?",
        "What's the busiest day of the week?",
        "How many orders did we receive yesterday?",
        "Which restaurant has the most loyal customers?",
        "What's the average order value by cuisine type?",
        "Show me customer reviews with ratings below 3",
        "Which menu items have the highest profit margins?",
        "What are the peak hours for orders?"
    ]
    
    for i, question in enumerate(sample_questions):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{i+1}.** {question}")
        with col2:
            if st.button("Try it!", key=f"sample_{i}"):
                st.session_state.selected_question = question
                st.session_state.page = "Natural Language Query"
                st.rerun()

def show_database_explorer():
    """Show database schema and sample data"""
    st.header("🗄️ Database Explorer")
    st.markdown("Explore the database schema and sample data:")
    
    conn = sqlite3.connect("restaurant_analytics.db")
    
    # Get table names
    tables = pd.read_sql_query(
        "SELECT name FROM sqlite_master WHERE type='table'", conn
    )['name'].tolist()
    
    selected_table = st.selectbox("Select a table to explore:", tables)
    
    if selected_table:
        # Show table schema
        st.subheader(f"📋 Schema for {selected_table}")
        schema = pd.read_sql_query(f"PRAGMA table_info({selected_table})", conn)
        st.dataframe(schema, use_container_width=True)
        
        # Show sample data
        st.subheader(f"📊 Sample Data from {selected_table}")
        sample_data = pd.read_sql_query(f"SELECT * FROM {selected_table} LIMIT 10", conn)
        st.dataframe(sample_data, use_container_width=True)
        
        # Show record count
        count = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {selected_table}", conn)
        st.info(f"Total records in {selected_table}: {count.iloc[0]['count']:,}")
    
    conn.close()

if __name__ == "__main__":
    main()