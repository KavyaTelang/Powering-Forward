import pandas as pd

# 1. Load the data
file_path = r"C:\Users\Kavya Telang\Downloads\archive (1)\organised_Gen.csv"  # Make sure this matches your file location
df = pd.read_csv(file_path)

# 2. Filter: Keep only the "Total Electric Power Industry" to capture the aggregate data
#    (The diagnostic showed this is the first value in 'TYPE OF PRODUCER')
df = df[df['TYPE OF PRODUCER'] == 'Total Electric Power Industry']

# 3. Create a clean 'Energy_Type' column based on the 'ENERGY SOURCE' column
#    We use string search because Solar might be named "Solar Thermal and Photovoltaic"
def categorize_source(source):
    source = str(source).lower()
    if 'wind' in source:
        return 'Wind'
    elif 'solar' in source:
        return 'Solar'
    else:
        return None

df['Energy_Type'] = df['ENERGY SOURCE'].apply(categorize_source)

# 4. Remove rows that aren't Solar or Wind
df_clean = df.dropna(subset=['Energy_Type'])

# 5. Group by Year and Energy Type, then sum the Generation
#    (Aggregating all states and months into one yearly total)
pivot_df = df_clean.groupby(['YEAR', 'Energy_Type'])['GENERATION (Megawatthours)'].sum().unstack(fill_value=0)

# 6. Convert MWh to TWh (1 Terawatt-hour = 1,000,000 Megawatt-hours)
pivot_df = pivot_df / 1_000_000

# 7. Rename columns to match your desired output
pivot_df.columns = [f"{col}_TWh" for col in pivot_df.columns]
pivot_df = pivot_df.reset_index().rename(columns={'YEAR': 'Year'})

# 8. Save and Print
print("Processed Data Preview:")
print(pivot_df.head())

pivot_df.to_csv('data/eia_renewable_data.csv', index=False)
print("\nSuccess! Saved to data/eia_renewable_data.csv")