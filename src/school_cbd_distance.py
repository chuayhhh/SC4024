import pandas as pd
import numpy as np

# Coordinates for key Central Hubs & Top Primary Schools
LOCATION_HUBS = {
    "CBD_Raffles": (1.283933, 103.851463),
    "Orchard_Hub": (1.303976, 103.831787),
    "Jurong_Regional_Center": (1.333152, 103.742286),
    "Woodlands_Regional_Center": (1.437021, 103.786376)
}

# Sample top-tier primary schools for family demand analysis
TOP_SCHOOLS = [
    {"school": "Nanyang Primary", "lat": 1.321151, "lon": 103.806540},
    {"school": "Tao Nan School", "lat": 1.304803, "lon": 103.905206},
    {"school": "Catholic High", "lat": 1.354780, "lon": 103.844900},
    {"school": "Henry Park Primary", "lat": 1.316870, "lon": 103.784230},
    {"school": "Raffles Girls Primary", "lat": 1.329880, "lon": 103.806200}
]

def haversine_np(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return 6367 * c

def compute_school_and_hub_distances(spatial_csv_path):
    print("Loading existing spatial feature dataset...")
    df_spatial = pd.read_csv(spatial_csv_path)
    
    valid_df = df_spatial.dropna(subset=['latitude', 'longitude']).copy()
    
    # 1. Distance to nearest top primary school
    school_df = pd.DataFrame(TOP_SCHOOLS)
    min_school_dists = []
    nearest_schools = []
    
    for _, row in valid_df.iterrows():
        lat, lon = row['latitude'], row['longitude']
        dists = haversine_np(lon, lat, school_df['lon'].values, school_df['lat'].values)
        min_idx = np.argmin(dists)
        min_school_dists.append(round(dists[min_idx], 3))
        nearest_schools.append(school_df.iloc[min_idx]['school'])
        
    valid_df['min_school_dist_km'] = min_school_dists
    valid_df['nearest_top_school'] = nearest_schools
    
    # 2. Distance to Regional Centers
    jurong_lat, jurong_lon = LOCATION_HUBS["Jurong_Regional_Center"]
    valid_df['jurong_hub_dist_km'] = haversine_np(
        valid_df['longitude'], valid_df['latitude'], jurong_lon, jurong_lat
    ).round(3)
    
    valid_df.to_csv(spatial_csv_path, index=False)
    print(f"✅ Updated spatial dataset with primary school & hub metrics: {spatial_csv_path}")

if __name__ == "__main__":
    compute_school_and_hub_distances("data/hdb_spatial_features.csv")
