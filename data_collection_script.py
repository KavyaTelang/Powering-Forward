"""
Custom EIA Data Processing Script for organized_Gen.csv
Processes Kaggle EIA dataset to extract Solar and Wind generation data
"""

import pandas as pd
import os

def process_organized_gen_file(filepath):
    """
    Process the organized_Gen.csv file from Kaggle
    
    Args:
        filepath: Path to organized_Gen.csv
    """
    print("📂 Loading organized_Gen.csv...")
    
    try:
        # Read the CSV file
        df = pd.read_csv(filepath)
        
        print(f"✅ File loaded successfully!")
        print(f"Shape: {df.shape}")
        print(f"\nColumns: {df.columns.tolist()}")
        print(f"\nFirst few rows:")
        print(df.head())
        
        # Check what energy types are available
        print("\n" + "="*70)
        print("AVAILABLE ENERGY TYPES:")
        print("="*70)
        energy_types = df['TYPE OF PRODUCER'].unique() if 'TYPE OF PRODUCER' in df.columns else df.iloc[:, 3].unique()
        for i, energy_type in enumerate(energy_types[:20], 1):  # Show first 20
            print(f"  {i}. {energy_type}")
        
        if len(energy_types) > 20:
            print(f"  ... and {len(energy_types) - 20} more")
        
        # Identify the correct column names
        print("\n" + "="*70)
        print("COLUMN IDENTIFICATION:")
        print("="*70)
        
        # Try to auto-detect columns
        year_col = 'YEAR' if 'YEAR' in df.columns else df.columns[0]
        type_col = 'TYPE OF PRODUCER' if 'TYPE OF PRODUCER' in df.columns else df.columns[3]
        gen_col = 'ENERGY SOURCE' if 'ENERGY SOURCE' in df.columns else df.columns[4]
        
        # Check if column names match what we see
        if 'GENERATION' in str(df.columns[-1]).upper():
            gen_col = df.columns[-1]
        
        print(f"Auto-detected columns:")
        print(f"  Year column: {year_col}")
        print(f"  Energy type column: {type_col}")
        print(f"  Generation column: {gen_col}")
        
        confirm = input("\nAre these correct? (yes/no): ").lower()
        
        if confirm != 'yes':
            print("\nPlease specify the column names:")
            year_col = input("Enter YEAR column name: ").strip()
            type_col = input("Enter ENERGY TYPE column name: ").strip()
            gen_col = input("Enter GENERATION column name: ").strip()
        
        # Filter for Solar and Wind
        print("\n" + "="*70)
        print("FILTERING DATA:")
        print("="*70)
        
        # Common patterns for solar and wind in EIA data
        solar_keywords = ['solar', 'photovoltaic', 'pv', 'sun']
        wind_keywords = ['wind']
        
        # Find solar entries
        solar_mask = df[type_col].str.lower().str.contains('|'.join(solar_keywords), na=False)
        solar_data = df[solar_mask].copy()
        
        print(f"Found {len(solar_data)} rows with Solar data")
        if len(solar_data) > 0:
            print(f"Solar types found: {solar_data[type_col].unique()}")
        
        # Find wind entries
        wind_mask = df[type_col].str.lower().str.contains('|'.join(wind_keywords), na=False)
        wind_data = df[wind_mask].copy()
        
        print(f"Found {len(wind_data)} rows with Wind data")
        if len(wind_data) > 0:
            print(f"Wind types found: {wind_data[type_col].unique()}")
        
        if len(solar_data) == 0 or len(wind_data) == 0:
            print("\n⚠️ Warning: Could not auto-detect Solar or Wind data")
            print("Please specify the exact text in the TYPE column:")
            solar_text = input("Enter the exact text for SOLAR (e.g., 'Solar Thermal and Photovoltaic'): ").strip()
            wind_text = input("Enter the exact text for WIND (e.g., 'Wind'): ").strip()
            
            solar_data = df[df[type_col] == solar_text].copy()
            wind_data = df[df[type_col] == wind_text].copy()
        
        # Aggregate by year
        print("\n" + "="*70)
        print("AGGREGATING DATA BY YEAR:")
        print("="*70)
        
        # Group by year and sum generation
        solar_yearly = solar_data.groupby(year_col)[gen_col].sum().reset_index()
        solar_yearly.columns = ['Year', 'Solar_Generation']
        
        wind_yearly = wind_data.groupby(year_col)[gen_col].sum().reset_index()
        wind_yearly.columns = ['Year', 'Wind_Generation']
        
        # Merge solar and wind data
        result_df = pd.merge(solar_yearly, wind_yearly, on='Year', how='outer')
        result_df = result_df.sort_values('Year')
        
        print(f"Aggregated to {len(result_df)} years")
        print(f"Year range: {result_df['Year'].min()} to {result_df['Year'].max()}")
        
        # Check units and convert if needed
        print("\n" + "="*70)
        print("UNIT CONVERSION:")
        print("="*70)
        print("Sample values:")
        print(result_df.head())
        
        unit_question = input("\nAre these values in MWh (megawatt-hours)? (yes/no): ").lower()
        
        if unit_question == 'yes':
            # Convert MWh to TWh (divide by 1,000,000 or 1000 depending on format)
            conversion = input("Divide by 1000 or 1000000? (usually 1000): ").strip()
            divisor = float(conversion) if conversion else 1000
            
            result_df['Solar_TWh'] = result_df['Solar_Generation'] / divisor
            result_df['Wind_TWh'] = result_df['Wind_Generation'] / divisor
        else:
            result_df['Solar_TWh'] = result_df['Solar_Generation']
            result_df['Wind_TWh'] = result_df['Wind_Generation']
        
        # Filter to 2014-2024
        filter_years = input("\nFilter to years 2014-2024 only? (yes/no): ").lower()
        if filter_years == 'yes':
            result_df = result_df[(result_df['Year'] >= 2014) & (result_df['Year'] <= 2024)]
            print(f"✅ Filtered to {len(result_df)} rows (2014-2024)")
        
        # Final dataset
        final_df = result_df[['Year', 'Solar_TWh', 'Wind_TWh']].copy()
        final_df = final_df.sort_values('Year').reset_index(drop=True)
        
        # Create data directory
        os.makedirs('data', exist_ok=True)
        
        # Save processed data
        output_path = 'data/eia_renewable_data.csv'
        final_df.to_csv(output_path, index=False)
        
        print("\n" + "="*70)
        print("✅ SUCCESS!")
        print("="*70)
        print(f"Processed data saved to: {output_path}")
        print(f"\nFinal dataset:")
        print(final_df)
        print(f"\nStats:")
        print(final_df.describe())
        
        return final_df
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_sample_data():
    """
    Create a sample dataset if processing fails
    """
    print("Creating sample dataset based on actual EIA trends...")
    
    data = {
        'Year': [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
        'Solar_TWh': [18.3, 26.5, 36.8, 52.9, 66.6, 71.3, 90.9, 115.6, 145.8, 163.6, 188.5],
        'Wind_TWh': [181.8, 190.7, 226.5, 254.3, 275.8, 303.4, 338.0, 379.5, 434.8, 425.2, 447.6]
    }
    
    df = pd.DataFrame(data)
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Save to CSV
    output_path = 'data/eia_renewable_data.csv'
    df.to_csv(output_path, index=False)
    
    print(f"✅ Sample dataset created: {output_path}")
    print(f"\nDataset Preview:")
    print(df)
    
    return df

def main():
    """
    Main function
    """
    print("="*70)
    print("EIA ORGANIZED_GEN.CSV PROCESSOR")
    print("="*70)
    print("\nThis script will process your Kaggle organized_Gen.csv file")
    print("and extract Solar & Wind generation data for 2014-2024.")
    print("\nChoose your option:")
    print("1. Process organized_Gen.csv file")
    print("2. Create sample dataset (for testing)")
    
    choice = input("\nEnter choice (1-2): ").strip()
    
    if choice == "1":
        print("\n" + "="*70)
        filepath = input("Enter the full path to organized_Gen.csv: ").strip()
        
        # Remove quotes if user copy-pasted path with quotes
        filepath = filepath.strip('"').strip("'")
        
        if os.path.exists(filepath):
            process_organized_gen_file(filepath)
        else:
            print(f"\n❌ File not found: {filepath}")
            print("\nTip: Make sure you entered the complete path including filename")
            print("Example: C:\\Users\\YourName\\Downloads\\organized_Gen.csv")
            
    elif choice == "2":
        create_sample_data()
        
    else:
        print("Invalid choice. Creating sample dataset...")
        create_sample_data()
    
    print("\n" + "="*70)
    print("✅ SETUP COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("1. Run your Streamlit app: streamlit run energy_analysis_app.py")
    print("2. Your app will load data from: data/eia_renewable_data.csv")
    print("\n")

if __name__ == "__main__":
    main()