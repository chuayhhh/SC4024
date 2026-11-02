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

def load_and_clean_hdb_data(file_path="data/resale_flat_prices_edited.csv"):
    print(f"Loading merged dataset from {file_path}...")
    df = pd.read_csv(file_path)
    
    # Standardize column headers
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    df = df.drop_duplicates()
    
    # -------------------------------------------------------------
    # SAFE CHECK FOR REMAINING LEASE
    # -------------------------------------------------------------
    if 'remaining_lease_years' not in df.columns:
        if 'remaining_lease' in df.columns:
            df['remaining_lease_years'] = df['remaining_lease'].apply(parse_remaining_lease)
        else:
            df['remaining_lease_years'] = np.nan
    else:
        # Ensure remaining_lease_years is numeric float
        df['remaining_lease_years'] = pd.to_numeric(df['remaining_lease_years'], errors='coerce')
    
    # Engineer derived metrics
    df['transaction_date'] = pd.to_datetime(df['month'], format='%Y-%m')
    df['transaction_year'] = df['transaction_date'].dt.year
    df['price_per_sqm'] = df['resale_price'] / df['floor_area_sqm']
    df['depreciation_per_year'] = df['resale_price'] / df['remaining_lease_years']
    
    # Map Weng Shi's column names to app.py expectations
    column_mapping = {
        'distance_to_mrt_km': 'min_mrt_dist_km',
        'nearest_mrt_station': 'nearest_mrt',
        'distance_to_cbd_km': 'cbd_dist_km',
        'full_address': 'address' 
    }
    df = df.rename(columns=column_mapping)
    
    # Merge spatial feature file if using old dataset
    spatial_path = pathlib.Path(file_path).parent / "hdb_spatial_features.csv"
    if 'min_mrt_dist_km' not in df.columns and spatial_path.exists():
        print("Merging spatial features (lat/lon, MRT, CBD distances)...")
        df_spatial = pd.read_csv(spatial_path)
        if 'address' not in df.columns:
            df['address'] = df['block'].astype(str) + " " + df['street_name'].astype(str)
        df = df.merge(df_spatial, on='address', how='left')

    print(f"✅ Data processing complete! Total records: {len(df):,}")
    return df

if __name__ == "__main__":
    df_test = load_and_clean_hdb_data("data/resale_flat_prices_edited.csv")
    print(df_test[['town', 'full_address', 'nearest_mrt', 'min_mrt_dist_km', 'cbd_dist_km']].head())
