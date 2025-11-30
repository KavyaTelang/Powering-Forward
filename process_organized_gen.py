import pandas as pd
import os

# Load the data
filepath = input("Enter path to organized_Gen.csv: ").strip().strip('"').strip("'")
df = pd.read_csv(filepath)

print("✅ File loaded!")
print(f"Total rows: {len(df)}")

# IMPORTANT: Filter for "Total Electric Power Industry" to avoid double-counting
print("\nFiltering for total industry values only...")
df = df[df['TYPE OF PRODUCER'] == 'Total Electric Power Industry']
print(f"Filtered to {len(df)} rows (Total Electric Power Industry only)")

# Now filter for Solar and Wind
print("\nFiltering for Solar and Wind...")

solar_df = df[df['ENERGY SOURCE'].str.contains('Solar', case=False, na=False)]
print(f"Found {len(solar_df)} Solar rows")

wind_df = df[df['ENERGY SOURCE'].str.contains('Wind', case=False, na=False)]
print(f"Found {len(wind_df)} Wind rows")

if len(solar_df) > 0:
    print(f"\nSolar energy sources: {solar_df['ENERGY SOURCE'].unique()}")
if len(wind_df) > 0:
    print(f"Wind energy sources: {wind_df['ENERGY SOURCE'].unique()}")

# Group by year and sum generation
print("\nAggregating by year...")

solar_yearly = solar_df.groupby('YEAR')['GENERATION (Megawatthours)'].sum()
wind_yearly = wind_df.groupby('YEAR')['GENERATION (Megawatthours)'].sum()

# Create final dataframe
result = pd.DataFrame({
    'Year': solar_yearly.index,
    'Solar_TWh': solar_yearly.values / 1000000,
    'Wind_TWh': wind_yearly.values / 1000000
})

# Filter to 2014-2024
result = result[(result['Year'] >= 2014) & (result['Year'] <= 2024)]
result = result.sort_values('Year').reset_index(drop=True)

print(f"\n✅ Processed data (2014-2024):")
print(result)
print("\nExpected: Solar ~18-188 TWh, Wind ~180-450 TWh")

# Save
os.makedirs('data', exist_ok=True)
result.to_csv('data/eia_renewable_data.csv', index=False)

print(f"\n✅ SUCCESS! Saved to: data/eia_renewable_data.csv")
print("\nNow run: streamlit run energy_analysis_app.py")