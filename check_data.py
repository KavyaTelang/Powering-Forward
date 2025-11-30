import pandas as pd

filepath = input("Enter path to organized_Gen.csv: ").strip().strip('"').strip("'")
df = pd.read_csv(filepath)

print("="*70)
print("COLUMN NAMES:")
print("="*70)
for i, col in enumerate(df.columns, 1):
    print(f"{i}. '{col}'")

print("\n" + "="*70)
print("FIRST 10 ROWS:")
print("="*70)
print(df.head(10))

print("\n" + "="*70)
print("UNIQUE ENERGY TYPES (first 30):")
print("="*70)

# Try to find the energy type column
for col in df.columns:
    if 'TYPE' in col.upper() or 'PRODUCER' in col.upper() or 'SOURCE' in col.upper():
        print(f"\nColumn: '{col}'")
        unique_values = df[col].unique()
        for i, val in enumerate(unique_values[:30], 1):
            print(f"  {i}. {val}")
        if len(unique_values) > 30:
            print(f"  ... and {len(unique_values) - 30} more")
        break