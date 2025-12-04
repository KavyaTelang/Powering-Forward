import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set page configuration
st.set_page_config(
    page_title="Powering Forward - Energy Analysis",
    page_icon="",
    layout="wide"
)

# Title and Header
st.title(" Powering Forward: U.S. Energy Growth Analysis")
st.write("Analyzing renewable energy trends from EIA data")

# LOAD DATA - REAL CSV ONLY
@st.cache_data
def load_data():
    """Load ONLY from CSV - no sample data fallback"""
    csv_path = 'data/eia_renewable_data.csv'
    
    # Check if file exists
    if not os.path.exists(csv_path):
        st.error(f"❌ CSV file not found at: {csv_path}")
        st.error("Please run the data processing script first!")
        st.stop()
    
    # Read CSV
    df = pd.read_csv(csv_path)
    
    # Validate data
    required_cols = ['Year', 'Solar_TWh', 'Wind_TWh']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"❌ Missing required columns: {missing_cols}")
        st.stop()
    
    # Calculate additional columns
    df['Total_Renewable'] = df['Solar_TWh'] + df['Wind_TWh']
    df['Solar_YoY_Growth'] = df['Solar_TWh'].pct_change() * 100
    df['Wind_YoY_Growth'] = df['Wind_TWh'].pct_change() * 100
    
    return df

# Load the data
df = load_data()

# Show data info in sidebar
st.sidebar.write("### Dataset Info")
st.sidebar.write(f" Years: {df['Year'].min()} - {df['Year'].max()}")
st.sidebar.write(f" {len(df)} Years of Data")
st.sidebar.write(f" Solar start: {df['Solar_TWh'].iloc[0]:.1f} TWh")
st.sidebar.write(f" Wind start: {df['Wind_TWh'].iloc[0]:.1f} TWh")

# Update the header with actual date range
st.write(f"**Data:** U.S. Energy Information Administration (EIA) via Kaggle | **Years:** {df['Year'].min()}-{df['Year'].max()}")
st.write("---")

# Calculate CAGR
def calculate_cagr(start_value, end_value, num_years):
    """Calculate Compound Annual Growth Rate"""
    cagr = (end_value / start_value) ** (1 / num_years) - 1
    return cagr * 100

solar_start = df['Solar_TWh'].iloc[0]
solar_end = df['Solar_TWh'].iloc[-1]
wind_start = df['Wind_TWh'].iloc[0]
wind_end = df['Wind_TWh'].iloc[-1]
num_years = df['Year'].iloc[-1] - df['Year'].iloc[0]

solar_cagr = calculate_cagr(solar_start, solar_end, num_years)
wind_cagr = calculate_cagr(wind_start, wind_end, num_years)

# Key Metrics Row
st.subheader("Key Growth Metrics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label=f" Solar CAGR",
        value=f"{solar_cagr:.2f}%",
        delta=f"+{solar_end - solar_start:.1f} TWh"
    )
    st.caption(f"{solar_start:.1f} → {solar_end:.1f} TWh ({num_years} years)")

with col2:
    st.metric(
        label=f" Wind CAGR",
        value=f"{wind_cagr:.2f}%",
        delta=f"+{wind_end - wind_start:.1f} TWh"
    )
    st.caption(f"{wind_start:.1f} → {wind_end:.1f} TWh ({num_years} years)")

with col3:
    st.metric(
        label=" Difference",
        value=f"{solar_cagr - wind_cagr:.2f}%"
    )
    st.caption("Solar growing faster")

st.write("---")

# Tabs for different visualizations
tab1, tab2, tab3, tab4 = st.tabs([
    "Generation Over Time", 
    "Growth Rate Comparison", 
    "Year-over-Year Changes",
    "Raw Data"
])

# Tab 1: Generation Overview
with tab1:
    st.write("### Energy Generation Trends")
    st.write(f"Looking at how solar and wind generation changed from {df['Year'].min()} to {df['Year'].max()}")
    
    # Set style
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot lines
    ax.plot(df['Year'], df['Solar_TWh'], marker='o', linewidth=3, 
            label='Solar', color='#ff8c00', markersize=8)
    ax.plot(df['Year'], df['Wind_TWh'], marker='s', linewidth=3, 
            label='Wind', color='#1f77b4', markersize=8)
    ax.plot(df['Year'], df['Total_Renewable'], marker='^', linewidth=2, 
            label='Total Renewable', color='#2ca02c', markersize=6, 
            linestyle='--', alpha=0.7)
    
    # Styling
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Energy Generation (TWh)', fontsize=12)
    ax.set_title('Solar vs Wind Generation', fontsize=14, pad=15)
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    st.write(f"**Note:** Solar grew from {solar_start:.1f} TWh to {solar_end:.1f} TWh (a {((solar_end/solar_start - 1)*100):.0f}% increase), while wind went from {wind_start:.1f} TWh to {wind_end:.1f} TWh ({((wind_end/wind_start - 1)*100):.0f}% increase). The growth patterns are pretty different.")

# Tab 2: CAGR Analysis
with tab2:
    st.write("### Comparing Growth Rates (CAGR)")
    st.write("CAGR = Compound Annual Growth Rate, basically the steady rate needed to go from start to end value")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    categories = ['Solar', 'Wind']
    values = [solar_cagr, wind_cagr]
    colors = ['#ff8c00', '#1f77b4']
    
    bars = ax.barh(categories, values, color=colors, alpha=0.7)
    
    # Add value labels
    for i, (bar, value) in enumerate(zip(bars, values)):
        ax.text(value + 0.3, i, f'{value:.2f}%', va='center', fontsize=12)
    
    ax.set_xlabel('CAGR (%)', fontsize=12)
    ax.set_title(f'Growth Rate Comparison ({df["Year"].min()}-{df["Year"].max()})', fontsize=13)
    ax.set_xlim(0, max(values) * 1.15)
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    st.pyplot(fig)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("** Solar**")
        st.write(f"CAGR: {solar_cagr:.2f}%")
        st.write("Growing fast probably because solar panels keep getting cheaper. Makes sense that adoption would accelerate.")
    
    with col2:
        st.write("** Wind**")
        st.write(f"CAGR: {wind_cagr:.2f}%")
        st.write("Slower growth rate but from a much bigger starting point. Wind has been around longer so less room for explosive growth.")

# Tab 3: YoY Trends
with tab3:
    st.write("### Year-over-Year Growth")
    st.write("How much did generation change each year compared to the previous year?")
    
    df_yoy = df[df['Year'] > df['Year'].min()].copy()
    
    fig, ax = plt.subplots(figsize=(12, 5))
    
    ax.plot(df_yoy['Year'], df_yoy['Solar_YoY_Growth'], 
            marker='o', linewidth=2, label='Solar YoY %', 
            color='#ff8c00', markersize=6)
    ax.plot(df_yoy['Year'], df_yoy['Wind_YoY_Growth'], 
            marker='s', linewidth=2, label='Wind YoY %', 
            color='#1f77b4', markersize=6)
    
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Growth Rate (%)', fontsize=12)
    ax.set_title('Annual Growth Rate Changes', fontsize=13)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    st.write("You can see the volatility year-to-year. Some years solar jumped a lot, other years less so.")
    
    with st.expander("How I processed the data"):
        st.write("""
        **Data Processing Steps:**
        1. Downloaded EIA data from Kaggle (organized_Gen.csv)
        2. Filtered for "Total Electric Power Industry" only (to avoid double-counting)
        3. Extracted rows where energy source contains "Solar" or "Wind"
        4. Grouped by year and summed across all states
        5. Converted from MWh to TWh (divided by 1,000,000)
        6. Calculated year-over-year growth using Pandas `.pct_change()`
        
        **Tools:** Python, Pandas, NumPy, Matplotlib, Seaborn, Streamlit
        """)

# Tab 4: Data Table
with tab4:
    st.write("### The Actual Numbers")
    
    # Format the dataframe for display
    display_df = df.copy()
    display_df['Solar_TWh'] = display_df['Solar_TWh'].round(1)
    display_df['Wind_TWh'] = display_df['Wind_TWh'].round(1)
    display_df['Total_Renewable'] = display_df['Total_Renewable'].round(1)
    display_df['Solar_YoY_Growth'] = display_df['Solar_YoY_Growth'].round(2)
    display_df['Wind_YoY_Growth'] = display_df['Wind_YoY_Growth'].round(2)
    
    st.dataframe(display_df, use_container_width=True)
    
    # Summary statistics
    st.write("### Quick Stats")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Solar:**")
        st.write(f"- Started at: {solar_start:.1f} TWh")
        st.write(f"- Ended at: {solar_end:.1f} TWh")
        st.write(f"- Total growth: {((solar_end - solar_start) / solar_start * 100):.0f}%")
        st.write(f"- CAGR: {solar_cagr:.2f}%")
    
    with col2:
        st.write("**Wind:**")
        st.write(f"- Started at: {wind_start:.1f} TWh")
        st.write(f"- Ended at: {wind_end:.1f} TWh")
        st.write(f"- Total growth: {((wind_end - wind_start) / wind_start * 100):.0f}%")
        st.write(f"- CAGR: {wind_cagr:.2f}%")

# Footer Section
st.write("---")
st.write("## What I Learned")

col1, col2 = st.columns(2)

with col1:
    st.write("**About the data:**")
    st.write(f"Solar's {solar_cagr:.1f}% growth rate is way higher than wind's {wind_cagr:.1f}%. This makes sense - solar panels have gotten a lot cheaper in recent years, so more people and companies are installing them. Wind was already pretty established when this data period started.")
    
with col2:
    st.write("**Why this matters:**")
    st.write("Understanding which renewable energy sources are growing fastest helps with planning investments and policy decisions. The fact that solar is accelerating so quickly suggests it's hitting a tipping point in adoption.")

# Sidebar
with st.sidebar:
    st.write("---")
    st.write("## Why I Built This")
    st.write("""
    I kept hearing about renewable energy growth but wanted to see the actual numbers myself. 
    
    Which is really growing faster - solar or wind? By how much?
    
    So I found EIA data on Kaggle, cleaned it up, and built this dashboard to explore the trends.
    
    **Main finding:** Solar is growing WAY faster than I expected (~15% annually vs wind's ~2%). 
    
    **What I did:**
    - Downloaded monthly state-level generation data
    - Cleaned it to avoid double-counting 
    - Aggregated to annual national totals
    - Calculated CAGR and other growth metrics
    - Built visualizations to see patterns
    
    The data was messier than expected - had to figure out the "Total Electric Power Industry" filtering to get accurate numbers. But that's part of working with real-world data.
    """)
    
    st.markdown("---")
    st.markdown("**Project by:** Kavya Telang")