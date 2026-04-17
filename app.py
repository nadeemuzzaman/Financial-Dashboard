"""
Vérexon Dashboard - Simple Financial Dashboard
A Streamlit application for analyzing revenue and cost data.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Vérexon Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 Vérexon Dashboard")
st.markdown("Analyze your financial data with interactive charts and metrics.")

# File uploader
uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=['xlsx', 'xls'],
    help="Upload an Excel file with Date, Revenue, and Cost columns"
)

def generate_dummy_data():
    """Generate dummy financial data for demonstration."""
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=30),
        end=datetime.now(),
        freq='D'
    )
    
    np.random.seed(42)
    revenues = 10000 + np.random.normal(0, 2000, len(dates)).cumsum()
    costs = 6000 + np.random.normal(0, 1500, len(dates)).cumsum()
    
    df = pd.DataFrame({
        'Date': dates,
        'Revenue': np.maximum(revenues, 0),
        'Cost': np.maximum(costs, 0)
    })
    
    df['Profit'] = df['Revenue'] - df['Cost']
    return df

# Load data
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        st.success(f"✅ File loaded successfully! ({len(df)} records)")
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        st.info("Using demo data instead.")
        df = generate_dummy_data()
else:
    df = generate_dummy_data()
    st.info("📋 Using demo data. Upload an Excel file to analyze your own data.")

# Display metrics
st.markdown("---")
st.subheader("📈 Financial Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_revenue = df['Revenue'].sum() if 'Revenue' in df.columns else 0
    st.metric("Total Revenue", f"${total_revenue:,.2f}")

with col2:
    total_cost = df['Cost'].sum() if 'Cost' in df.columns else 0
    st.metric("Total Cost", f"${total_cost:,.2f}")

with col3:
    profit = total_revenue - total_cost
    st.metric("Total Profit", f"${profit:,.2f}")

with col4:
    profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
    st.metric("Profit Margin", f"{profit_margin:.2f}%")

# Line chart
st.markdown("---")
st.subheader("📊 Financial Trends")

# Prepare data for chart
if 'Date' in df.columns and 'Revenue' in df.columns and 'Cost' in df.columns:
    chart_data = df[['Date', 'Revenue', 'Cost']].copy()
    chart_data = chart_data.set_index('Date')
    
    st.line_chart(chart_data)
    
    # Add profit chart if profit column exists
    if 'Profit' in df.columns:
        profit_chart_data = df[['Date', 'Profit']].copy()
        profit_chart_data = profit_chart_data.set_index('Date')
        st.line_chart(profit_chart_data)
else:
    st.warning("Required columns (Date, Revenue, Cost) not found in the data.")

# Data table
st.markdown("---")
st.subheader("📋 Data Table")

if 'Date' in df.columns:
    df_display = df.copy()
    df_display['Date'] = df_display['Date'].dt.strftime('%Y-%m-%d')
    
    # Format numeric columns
    for col in ['Revenue', 'Cost', 'Profit']:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "")
    
    st.dataframe(df_display, use_container_width=True)
else:
    st.dataframe(df, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Vérexon Dashboard v1.0 | Built with Streamlit")