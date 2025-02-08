import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from utils import fetch_energy_data, process_pricing_data

# Page configuration
st.set_page_config(
    page_title="Energy Pricing Dashboard",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
    .big-font {
        font-size:24px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("⚡ Energy Pricing Dashboard")

# Add location and circuit information
st.markdown("""
<div style='background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
    <p style='margin: 0; font-size: 1.1rem;'>
        📍 <strong>Location:</strong> San Francisco<br>
        🔌 <strong>Circuit ID:</strong> 24040403
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Date range selector
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input(
        "Start Date",
        datetime.now().date(),
        min_value=datetime.now().date() - timedelta(days=365),
        max_value=datetime.now().date() + timedelta(days=365)
    )
with col2:
    end_date = st.date_input(
        "End Date",
        datetime.now().date(),
        min_value=start_date,
        max_value=datetime.now().date() + timedelta(days=365)
    )

# Fetch data button
if st.button("Fetch Pricing Data"):
    try:
        with st.spinner('Fetching data...'):
            # Convert dates to required format (YYYYMMDD)
            start_str = start_date.strftime('%Y%m%d')
            end_str = end_date.strftime('%Y%m%d')
            
            # Fetch data
            data = fetch_energy_data(start_str, end_str)
            
            if data:
                # Process the data
                df = process_pricing_data(data)
                
                # Display summary statistics
                st.subheader("Summary Statistics")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Average Price", f"${df['price'].mean():.2f}/kWh")
                with col2:
                    st.metric("Max Price", f"${df['price'].max():.2f}/kWh")
                with col3:
                    st.metric("Min Price", f"${df['price'].min():.2f}/kWh")
                
                # Plot the data
                st.subheader("Price Trends")
                fig = px.line(
                    df,
                    x='datetime',
                    y='price',
                    title='Energy Pricing Over Time',
                    labels={'datetime': 'Date & Time', 'price': 'Price ($/kWh)'}
                )
                fig.update_layout(
                    xaxis_title="Date & Time",
                    yaxis_title="Price ($/kWh)",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Display raw data
                st.subheader("Raw Data")
                st.dataframe(df)
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download Data as CSV",
                    data=csv,
                    file_name=f"energy_pricing_{start_str}_to_{end_str}.csv",
                    mime="text/csv"
                )
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Data provided by GridX Energy Pricing API")