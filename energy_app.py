import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set page configuration
st.set_page_config(
    page_title="Powering Forward - Energy Analysis",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and Header
st.markdown('<p class="main-header">⚡ Powering Forward</p>', unsafe_allow_html=True)
st.markdown("### A Vector Analysis of U.S. Energy Growth")

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
st.sidebar.success(f"✅ Real Kaggle EIA Data Loaded")
st.sidebar.metric("Total Years", len(df))
st.sidebar.metric("Date Range", f"{df['Year'].min()} - {df['Year'].max()}")
st.sidebar.metric("First Solar Value", f"{df['Solar_TWh'].iloc[0]:.1f} TWh")

# Update the header with actual date range
st.markdown(f"**Data Source:** U.S. Energy Information Administration (EIA) via Kaggle | **Period:** {df['Year'].min()}-{df['Year'].max()}")
st.markdown("---")

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
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label=f"☀️ Solar CAGR ({num_years}-Year)",
        value=f"{solar_cagr:.2f}%",
        delta=f"{solar_end - solar_start:.1f} TWh growth"
    )
    st.caption(f"From {solar_start:.1f} to {solar_end:.1f} TWh")

with col2:
    st.metric(
        label=f"💨 Wind CAGR ({num_years}-Year)",
        value=f"{wind_cagr:.2f}%",
        delta=f"{wind_end - wind_start:.1f} TWh growth"
    )
    st.caption(f"From {wind_start:.1f} to {wind_end:.1f} TWh")

with col3:
    st.metric(
        label="📈 Growth Differential",
        value=f"{solar_cagr - wind_cagr:.2f}%",
        delta="Solar leads Wind"
    )
    st.caption("Accelerating momentum")

st.markdown("---")

# Tabs for different visualizations
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Generation Overview", 
    "📈 CAGR Analysis", 
    "📉 YoY Trends",
    "📋 Data Table"
])

# Tab 1: Generation Overview
with tab1:
    st.subheader(f"Renewable Energy Generation Trends ({df['Year'].min()}-{df['Year'].max()})")
    
    # Set style
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Plot lines
    ax.plot(df['Year'], df['Solar_TWh'], marker='o', linewidth=3, 
            label='Solar', color='#ff8c00', markersize=8)
    ax.plot(df['Year'], df['Wind_TWh'], marker='s', linewidth=3, 
            label='Wind', color='#1f77b4', markersize=8)
    ax.plot(df['Year'], df['Total_Renewable'], marker='^', linewidth=2, 
            label='Total Renewable', color='#2ca02c', markersize=6, 
            linestyle='--', alpha=0.7)
    
    # Styling
    ax.set_xlabel('Year', fontsize=14, fontweight='bold')
    ax.set_ylabel('Energy Generation (TWh)', fontsize=14, fontweight='bold')
    ax.set_title('U.S. Renewable Energy Generation (Real Kaggle EIA Data)', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.legend(fontsize=12, loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.set_xticks(df['Year'])
    
    # Add annotation
    ax.annotate(f'Solar: {solar_end:.1f} TWh', 
                xy=(df['Year'].iloc[-1], solar_end),
                xytext=(10, 20), textcoords='offset points',
                fontsize=11, color='#ff8c00',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8),
                arrowprops=dict(arrowstyle='->', color='#ff8c00', lw=2))
    
    plt.tight_layout()
    st.pyplot(fig)
    
    st.info(f"**What I Found:** Solar generation grew from {solar_start:.1f} TWh to {solar_end:.1f} TWh (a {((solar_end/solar_start - 1)*100):.0f}% increase), while wind grew from {wind_start:.1f} TWh to {wind_end:.1f} TWh ({((wind_end/wind_start - 1)*100):.0f}% increase). The difference in growth trajectories is striking.")

# Tab 2: CAGR Analysis
with tab2:
    st.subheader("Compound Annual Growth Rate (CAGR) Comparison")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    categories = ['Solar CAGR', 'Wind CAGR']
    values = [solar_cagr, wind_cagr]
    colors = ['#ff8c00', '#1f77b4']
    
    bars = ax.barh(categories, values, color=colors, height=0.5, alpha=0.8)
    
    # Add value labels
    for i, (bar, value) in enumerate(zip(bars, values)):
        ax.text(value + 0.5, i, f'{value:.2f}%', 
                va='center', fontsize=14, fontweight='bold')
    
    ax.set_xlabel('Compound Annual Growth Rate (%)', fontsize=13, fontweight='bold')
    ax.set_title(f'CAGR Comparison: Solar vs Wind ({df["Year"].min()}-{df["Year"].max()})', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlim(0, max(values) * 1.2)
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    st.pyplot(fig)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ☀️ Solar Growth")
        st.write(f"**CAGR: {solar_cagr:.2f}%**")
        st.write("Solar is growing fast because the technology keeps getting cheaper. What used to be expensive is now cost-competitive with traditional energy sources, which is driving rapid adoption.")
    
    with col2:
        st.markdown("#### 💨 Wind Growth")
        st.write(f"**CAGR: {wind_cagr:.2f}%**")
        st.write("Wind has been around longer and is more established. The growth rate is lower because we're adding to an already large base - but it's still growing steadily.")

# Tab 3: YoY Trends
with tab3:
    st.subheader("Year-over-Year Growth Rates")
    
    df_yoy = df[df['Year'] > df['Year'].min()].copy()
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    ax.plot(df_yoy['Year'], df_yoy['Solar_YoY_Growth'], 
            marker='o', linewidth=2.5, label='Solar YoY%', 
            color='#ff8c00', markersize=8)
    ax.plot(df_yoy['Year'], df_yoy['Wind_YoY_Growth'], 
            marker='s', linewidth=2.5, label='Wind YoY%', 
            color='#1f77b4', markersize=8)
    
    ax.axhline(y=0, color='red', linestyle='--', alpha=0.3, linewidth=1)
    
    ax.set_xlabel('Year', fontsize=13, fontweight='bold')
    ax.set_ylabel('Year-over-Year Growth Rate (%)', fontsize=13, fontweight='bold')
    ax.set_title('Renewable Energy YoY Growth Volatility', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.legend(fontsize=12, loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_xticks(df_yoy['Year'])
    
    plt.tight_layout()
    st.pyplot(fig)
    
    with st.expander("📊 Methodology & Data Processing"):
        st.markdown(f"""
        - **Data Source:** Kaggle dataset of U.S. EIA renewable energy generation
        - **Processing:** Filtered for "Total Electric Power Industry" to avoid double-counting
        - **Aggregation:** Summed monthly state-level data to annual national totals
        - **Unit Conversion:** Converted from Megawatt-hours (MWh) to Terawatt-hours (TWh)
        - **CAGR Formula:** (End Value / Start Value)^(1 / Years) - 1
        - **Time Period:** {df['Year'].min()} to {df['Year'].max()} ({num_years} years)
        - **Tools:** Python, Pandas, NumPy, Matplotlib, Seaborn, Streamlit
        """)

# Tab 4: Data Table
with tab4:
    st.subheader("Complete Dataset")
    
    # Format the dataframe for display
    display_df = df.copy()
    display_df['Solar_TWh'] = display_df['Solar_TWh'].round(1)
    display_df['Wind_TWh'] = display_df['Wind_TWh'].round(1)
    display_df['Total_Renewable'] = display_df['Total_Renewable'].round(1)
    display_df['Solar_YoY_Growth'] = display_df['Solar_YoY_Growth'].round(2)
    display_df['Wind_YoY_Growth'] = display_df['Wind_YoY_Growth'].round(2)
    
    st.dataframe(display_df, use_container_width=True)
    
    # Summary statistics
    st.subheader("Summary Statistics")
    
    summary_data = {
        'Metric': [
            f'Starting Value ({df["Year"].min()})',
            f'Ending Value ({df["Year"].max()})',
            'Total Growth',
            'CAGR',
            'Average Annual Increase',
            'Peak YoY Growth',
        ],
        'Solar': [
            f"{solar_start:.1f} TWh",
            f"{solar_end:.1f} TWh",
            f"{((solar_end - solar_start) / solar_start * 100):.1f}%",
            f"{solar_cagr:.2f}%",
            f"{(solar_end - solar_start) / num_years:.1f} TWh/year",
            f"{df_yoy['Solar_YoY_Growth'].max():.1f}%",
        ],
        'Wind': [
            f"{wind_start:.1f} TWh",
            f"{wind_end:.1f} TWh",
            f"{((wind_end - wind_start) / wind_start * 100):.1f}%",
            f"{wind_cagr:.2f}%",
            f"{(wind_end - wind_start) / num_years:.1f} TWh/year",
            f"{df_yoy['Wind_YoY_Growth'].max():.1f}%",
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)

# Footer Section
st.markdown("---")
st.subheader("🔑 My Takeaways")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### ☀️ Solar Is Accelerating")
    st.write(f"Solar's **{solar_cagr:.1f}%** growth rate far exceeds wind's **{wind_cagr:.1f}%**. This makes sense given how much solar panel costs have dropped - they're now cheaper than ever for both utilities and homeowners.")

with col2:
    st.markdown("#### 💨 Wind Is Steady")
    st.write(f"Wind grew **{((wind_end - wind_start) / wind_start * 100):.0f}%** over this period, but from a much larger base. It's a more mature technology, so the explosive growth phase has passed.")

with col3:
    st.markdown("#### 📊 The Big Picture")
    st.write(f"Together, solar and wind went from **{(solar_start + wind_start):.1f} TWh** to **{(solar_end + wind_end):.1f} TWh**. That's real progress toward cleaner energy, though there's still a long way to go.")

# Sidebar
with st.sidebar:
    st.markdown("---")
    st.title("💡 Project Motivation")
    st.markdown("""
    I wanted to understand which renewable energy source is actually growing faster in the U.S. - solar or wind.
    
    With all the talk about clean energy transitions, I was curious to see the data for myself and quantify the real momentum behind each technology.
    
    **What I Did:**
    - Found EIA generation data on Kaggle
    - Cleaned and processed monthly state-level data
    - Aggregated to annual national totals
    - Calculated growth metrics (CAGR, YoY)
    - Built this dashboard to explore the trends
    
    **What I Learned:**
    The numbers surprised me. Solar is growing much faster than I expected, while wind growth has been more gradual. This tells me solar technology has hit an inflection point in cost and adoption.
    
    **Why This Matters:**
    Understanding these growth patterns helps inform investment decisions, policy planning, and gives us a clearer picture of America's energy future.
    """)
    
    st.markdown("---")
    st.markdown("**Project by:** Kavya Telang")
    st.markdown("**GitHub:** [Your Repo]")