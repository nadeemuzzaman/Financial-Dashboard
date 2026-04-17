"""
Smart Financial Dashboard
A Streamlit application for analyzing revenue and cost data from Excel files.
Author: Finance Professional
Date: 2024
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io

# Page configuration
st.set_page_config(
    page_title="Smart Financial Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F8F9FA;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1E3A8A;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .positive {
        color: #10B981;
        font-weight: bold;
    }
    .negative {
        color: #EF4444;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def generate_dummy_data():
    """
    Generate dummy financial data for demonstration purposes.
    Returns a pandas DataFrame with Date, Revenue, and Cost columns.
    """
    # Generate dates for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=29)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate random revenue and cost data
    np.random.seed(42)  # For reproducibility
    base_revenue = 10000
    revenue_trend = np.linspace(0, 0.2, 30)  # 20% growth over 30 days
    revenue_noise = np.random.normal(0, 500, 30)
    revenues = base_revenue * (1 + revenue_trend) + revenue_noise
    
    # Costs are typically 60-80% of revenue
    cost_ratio = np.random.uniform(0.6, 0.8, 30)
    costs = revenues * cost_ratio
    
    # Create DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Revenue': np.round(revenues, 2),
        'Cost': np.round(costs, 2)
    })
    
    return df

def load_excel_data(uploaded_file):
    """
    Load and validate Excel file data.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    
    Returns:
        pandas DataFrame if successful, None if error
    """
    try:
        # Read Excel file
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        # Validate required columns
        required_columns = ['Date', 'Revenue', 'Cost']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Missing required columns: {', '.join(missing_columns)}")
            st.info("Please ensure your Excel file has columns named: Date, Revenue, Cost")
            return None
        
        # Convert Date column to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Validate numeric columns
        df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce')
        df['Cost'] = pd.to_numeric(df['Cost'], errors='coerce')
        
        # Drop rows with missing values in critical columns
        df = df.dropna(subset=['Date', 'Revenue', 'Cost'])
        
        return df
    
    except Exception as e:
        st.error(f"Error loading Excel file: {str(e)}")
        return None

def calculate_metrics(df):
    """
    Calculate financial metrics from the DataFrame.
    
    Args:
        df: pandas DataFrame with Revenue and Cost columns
    
    Returns:
        Dictionary containing calculated metrics
    """
    metrics = {}
    
    # Calculate basic metrics
    metrics['total_revenue'] = df['Revenue'].sum()
    metrics['total_cost'] = df['Cost'].sum()
    metrics['profit'] = metrics['total_revenue'] - metrics['total_cost']
    
    # Calculate profit margin (handle division by zero)
    if metrics['total_revenue'] > 0:
        metrics['profit_margin'] = (metrics['profit'] / metrics['total_revenue']) * 100
    else:
        metrics['profit_margin'] = 0
    
    # Calculate additional metrics
    metrics['avg_daily_revenue'] = df['Revenue'].mean()
    metrics['avg_daily_cost'] = df['Cost'].mean()
    metrics['data_points'] = len(df)
    
    return metrics

def format_currency(value):
    """
    Format numeric value as currency.
    
    Args:
        value: Numeric value to format
    
    Returns:
        Formatted currency string
    """
    if value >= 0:
        return f"${value:,.2f}"
    else:
        return f"-${abs(value):,.2f}"

def format_percentage(value):
    """
    Format numeric value as percentage.
    
    Args:
        value: Numeric value to format
    
    Returns:
        Formatted percentage string
    """
    return f"{value:.2f}%"

def display_metrics(metrics):
    """
    Display financial metrics as cards in the dashboard.
    
    Args:
        metrics: Dictionary containing calculated metrics
    """
    # Create columns for metric cards
    col1, col2, col3, col4 = st.columns(4)
    
    # Revenue Card
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Total Revenue",
            value=format_currency(metrics['total_revenue']),
            delta=None
        )
        st.caption(f"Avg Daily: {format_currency(metrics['avg_daily_revenue'])}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Cost Card
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Total Cost",
            value=format_currency(metrics['total_cost']),
            delta=None
        )
        st.caption(f"Avg Daily: {format_currency(metrics['avg_daily_cost'])}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Profit Card
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        profit_class = "positive" if metrics['profit'] >= 0 else "negative"
        st.markdown(f'<div class="{profit_class}">', unsafe_allow_html=True)
        st.metric(
            label="Total Profit",
            value=format_currency(metrics['profit']),
            delta=None
        )
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption(f"Revenue - Cost")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Profit Margin Card
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        margin_class = "positive" if metrics['profit_margin'] >= 0 else "negative"
        st.markdown(f'<div class="{margin_class}">', unsafe_allow_html=True)
        st.metric(
            label="Profit Margin",
            value=format_percentage(metrics['profit_margin']),
            delta=None
        )
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption(f"Profit / Revenue")
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    """
    Main application function.
    """
    # Application header
    st.markdown('<h1 class="main-header">📊 Smart Financial Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("Analyze your revenue and cost data to calculate key financial metrics.")
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("Data Input")
        st.markdown("---")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload Excel File",
            type=['xlsx', 'xls'],
            help="Upload an Excel file with columns: Date, Revenue, Cost"
        )
        
        st.markdown("---")
        st.info("""
        **File Requirements:**
        - Excel format (.xlsx or .xls)
        - Required columns: Date, Revenue, Cost
        - Date column should be in date format
        - Revenue and Cost should be numeric values
        """)
        
        # Data source selection
        use_dummy_data = st.checkbox(
            "Use demo data",
            value=(uploaded_file is None),
            help="Generate dummy data for demonstration"
        )
    
    # Load data based on user selection
    if uploaded_file is not None and not use_dummy_data:
        # Load uploaded Excel file
        df = load_excel_data(uploaded_file)
        data_source = "Uploaded File"
        
        if df is None:
            st.warning("Using demo data instead due to file loading issues.")
            df = generate_dummy_data()
            data_source = "Demo Data (Fallback)"
            use_dummy_data = True
    else:
        # Generate dummy data
        df = generate_dummy_data()
        data_source = "Demo Data"
        use_dummy_data = True
    
    # Display data source information
    if use_dummy_data:
        st.info(f"📋 Currently showing: **{data_source}** | {len(df)} records")
        st.download_button(
            label="📥 Download Sample Data",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name="sample_financial_data.csv",
            mime="text/csv",
            help="Download the generated sample data as CSV"
        )
    else:
        st.success(f"✅ Data loaded from: **{data_source}** | {len(df)} records")
    
    # Calculate metrics
    metrics = calculate_metrics(df)
    
    # Display metrics section
    st.markdown("---")
    st.subheader("📈 Financial Metrics")
    display_metrics(metrics)
    
    # Display data table
    st.markdown("---")
    st.subheader("📋 Data Table")
    
    # Add some data summary
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Date Range:** {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")
    with col2:
        st.write(f"**Records:** {len(df)}")
    
    # Display the data table with formatting
    df_display = df.copy()
    df_display['Date'] = df_display['Date'].dt.strftime('%Y-%m-%d')
    df_display['Revenue'] = df_display['Revenue'].apply(format_currency)
    df_display['Cost'] = df_display['Cost'].apply(format_currency)
    
    # Calculate profit for display
    df_display['Profit'] = df['Revenue'] - df['Cost']
    df_display['Profit'] = df_display['Profit'].apply(format_currency)
    
    st.dataframe(df_display, use_container_width=True)
    
    # Additional insights section
    st.markdown("---")
    st.subheader("💡 Insights")
    
    # Generate insights based on data
    if metrics['profit_margin'] > 20:
        st.success(f"**Strong Performance:** Your profit margin of {format_percentage(metrics['profit_margin'])} indicates healthy financial performance.")
    elif metrics['profit_margin'] > 0:
        st.info(f"**Positive Margin:** Your profit margin is {format_percentage(metrics['profit_margin'])}. Consider optimizing costs to improve.")
    else:
        st.warning(f"**Attention Needed:** Negative profit margin of {format_percentage(metrics['profit_margin'])}. Review costs and revenue strategies.")
    
    # Cost efficiency insight
    cost_ratio = (metrics['total_cost'] / metrics['total_revenue']) * 100 if metrics['total_revenue'] > 0 else 100
    st.write(f"**Cost Efficiency:** Costs represent {cost_ratio:.1f}% of revenue.")
    
    # Footer
    st.markdown("---")
    st.caption("Smart Financial Dashboard v1.0 | Built with Streamlit")

if __name__ == "__main__":
    main()