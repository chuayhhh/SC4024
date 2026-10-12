import pandas as pd
import numpy as np
import pathlib

def parse_remaining_lease(lease_str):
    if pd.isna(lease_str):
        return np.nan
    if isinstance(lease_str, (int, float)):
        return float(lease_str)
        
    parts = str(lease_str).strip().split()
    years = 0
    months = 0
    
    try:
        if 'years' in parts or 'year' in parts:
            years = int(parts[0])
            if 'months' in parts or 'month' in parts:
                months = int(parts[2])
        elif 'months' in parts or 'month' in parts:
            months = int(parts[0])
        return round(years + (months / 12.0), 2)
    except (IndexError, ValueError):
        return np.nan

def load_and_clean_hdb_data(file_path):
    print(f"Loading base dataset from {file_path}...")
    df = pd.read_csv(file_path)
    
    # Standardize column headers
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    df = df.drop_duplicates()
    
    # Engineer base metrics
    df['remaining_lease_years'] = df['remaining_lease'].apply(parse_remaining_lease)
    df['transaction_date'] = pd.to_datetime(df['month'], format='%Y-%m')
    df['transaction_year'] = df['transaction_date'].dt.year
    df['price_per_sqm'] = df['resale_price'] / df['floor_area_sqm']
    df['depreciation_per_year'] = df['resale_price'] / df['remaining_lease_years']
    
    # Create matching address key
    df['address'] = df['block'].astype(str) + " " + df['street_name'].astype(str)
    
    # Merge spatial dataset if available
    spatial_path = pathlib.Path(file_path).parent / "hdb_spatial_features.csv"
    if spatial_path.exists():
        print("Merging spatial features (lat/lon, MRT, CBD distances)...")
        df_spatial = pd.read_csv(spatial_path)
        df = df.merge(df_spatial, on='address', how='left')
    else:
        print("⚠️ Spatial feature file not found. Proceeding without geospatial columns.")
        
    print(f"✅ Data processing complete! Total records: {len(df):,}")
    return df

if __name__ == "__main__":
    df_test = load_and_clean_hdb_data("data/resale_flat_prices.csv")
    print(df_test[['town', 'address', 'nearest_mrt', 'min_mrt_dist_km', 'cbd_dist_km']].head())
