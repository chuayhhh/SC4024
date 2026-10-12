import pandas as pd
import numpy as np

# Coordinates for key Singapore MRT Stations across NS, EW, NE, CC, DT, TE lines
MRT_STATIONS = [
    {"station": "Jurong East", "lat": 1.333152, "lon": 103.742286},
    {"station": "Bukit Batok", "lat": 1.349035, "lon": 103.749526},
    {"station": "Bukit Gombak", "lat": 1.358611, "lon": 103.751791},
    {"station": "Choa Chu Kang", "lat": 1.385363, "lon": 103.744371},
    {"station": "Yew Tee", "lat": 1.397476, "lon": 103.747424},
    {"station": "Yishun", "lat": 1.429443, "lon": 103.835008},
    {"station": "Khatib", "lat": 1.417383, "lon": 103.832980},
    {"station": "Yio Chu Kang", "lat": 1.381756, "lon": 103.844947},
    {"station": "Ang Mo Kio", "lat": 1.369933, "lon": 103.849558},
    {"station": "Bishan", "lat": 1.350839, "lon": 103.848140},
    {"station": "Braddell", "lat": 1.340469, "lon": 103.846799},
    {"station": "Toa Payoh", "lat": 1.332702, "lon": 103.847575},
    {"station": "Novena", "lat": 1.320440, "lon": 103.843825},
    {"station": "Newton", "lat": 1.312310, "lon": 103.837984},
    {"station": "Orchard", "lat": 1.303976, "lon": 103.831787},
    {"station": "Somerset", "lat": 1.300207, "lon": 103.839084},
    {"station": "Dhoby Ghaut", "lat": 1.299704, "lon": 103.845445},
    {"station": "City Hall", "lat": 1.292936, "lon": 103.852586},
    {"station": "Raffles Place", "lat": 1.283933, "lon": 103.851463},
    {"station": "Marina Bay", "lat": 1.276413, "lon": 103.854598},
    {"station": "Bugis", "lat": 1.300772, "lon": 103.855823},
    {"station": "Paya Lebar", "lat": 1.318183, "lon": 103.892881},
    {"station": "Tampines", "lat": 1.352693, "lon": 103.945322},
    {"station": "Pasir Ris", "lat": 1.373043, "lon": 103.949316},
    {"station": "Clementi", "lat": 1.315116, "lon": 103.765239},
    {"station": "Buona Vista", "lat": 1.307373, "lon": 103.790030},
    {"station": "Outram Park", "lat": 1.280228, "lon": 103.839486},
    {"station": "Serangoon", "lat": 1.349603, "lon": 103.873558},
    {"station": "Punggol", "lat": 1.405299, "lon": 103.902318},
    {"station": "Sengkang", "lat": 1.391695, "lon": 103.895482},
    {"station": "Woodlands", "lat": 1.437021, "lon": 103.786376}
]

def haversine_np(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points on earth in kilometers.
    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    return km

def compute_spatial_distances(coords_csv_path, output_spatial_path):
    print("Loading HDB coordinates dataset...")
    df_coords = pd.read_csv(coords_csv_path)
    
    # Filter valid coordinates
    valid_df = df_coords.dropna(subset=['latitude', 'longitude']).copy()
    
    mrt_df = pd.DataFrame(MRT_STATIONS)
    
    min_distances = []
    nearest_stations = []
    
    print("Computing distance to nearest MRT station...")
    for _, row in valid_df.iterrows():
        lat, lon = row['latitude'], row['longitude']
        
        # Distance to all MRTs
        distances = haversine_np(lon, lat, mrt_df['lon'].values, mrt_df['lat'].values)
        min_idx = np.argmin(distances)
        
        min_distances.append(round(distances[min_idx], 3))
        nearest_stations.append(mrt_df.iloc[min_idx]['station'])
        
    valid_df['min_mrt_dist_km'] = min_distances
    valid_df['nearest_mrt'] = nearest_stations
    
    # Distance to CBD (Raffles Place MRT)
    cbd_lat, cbd_lon = 1.283933, 103.851463
    valid_df['cbd_dist_km'] = haversine_np(valid_df['longitude'], valid_df['latitude'], cbd_lon, cbd_lat).round(3)
    
    valid_df.to_csv(output_spatial_path, index=False)
    print(f"✅ Spatial distance dataset saved to {output_spatial_path}!")
    print("\nPreview of spatial feature output:")
    print(valid_df[['address', 'nearest_mrt', 'min_mrt_dist_km', 'cbd_dist_km']].head())

if __name__ == "__main__":
    compute_spatial_distances("data/hdb_coordinates.csv", "data/hdb_spatial_features.csv")
