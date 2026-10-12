import pandas as pd
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_coordinates_public(addr_info):
    """
    Worker function to fetch latitude and longitude for a single address.
    """
    addr, block, street_name = addr_info
    onemap_url = f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={block}%20{street_name}&returnGeom=Y&getAddrDetails=Y&pageNum=1"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
    }
    
    # 1st attempt: OneMap Public Endpoint
    try:
        response = requests.get(onemap_url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('found', 0) > 0 and len(data.get('results', [])) > 0:
                result = data['results'][0]
                return addr, float(result['LATITUDE']), float(result['LONGITUDE'])
    except Exception:
        pass

    # 2nd attempt: Nominatim Fallback
    search_val = f"{block} {street_name} SINGAPORE"
    nominatim_url = f"https://nominatim.openstreetmap.org/search?q={requests.utils.quote(search_val)}&format=json&limit=1"
    try:
        response = requests.get(nominatim_url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 0:
                return addr, float(data[0]['lat']), float(data[0]['lon'])
    except Exception:
        pass

    return addr, None, None

def generate_all_hdb_coordinates(hdb_csv_path, output_coords_path):
    print("Reading HDB transaction dataset...")
    df = pd.read_csv(hdb_csv_path)
    
    df['address'] = df['block'].astype(str) + " " + df['street_name'].astype(str)
    
    # Extract unique address tuples (address, block, street_name)
    unique_df = df[['address', 'block', 'street_name']].drop_duplicates()
    address_tuples = [tuple(x) for x in unique_df.to_numpy()]
    
    total_addresses = len(address_tuples)
    print(f"Total transaction rows: {len(df):,}")
    print(f"Unique physical addresses to geocode: {total_addresses:,}")
    print("\n--- Starting Parallel Geocoding (This will take ~2-3 mins) ---")
    
    coords_dict = {}
    completed = 0
    successful = 0
    
    # Use ThreadPoolExecutor for fast parallel requests
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(get_coordinates_public, item) for item in address_tuples]
        
        for future in as_completed(futures):
            addr, lat, lon = future.result()
            coords_dict[addr] = {'latitude': lat, 'longitude': lon}
            completed += 1
            if lat is not None:
                successful += 1
                
            if completed % 500 == 0 or completed == total_addresses:
                print(f"Progress: {completed}/{total_addresses} ({completed/total_addresses*100:.1f}%) | Success: {successful}")

    print(f"\n✅ Full Geocoding Complete! Success Rate: {successful}/{total_addresses} ({successful/total_addresses*100:.1f}%)")
    
    coords_df = pd.DataFrame.from_dict(coords_dict, orient='index').reset_index()
    coords_df.columns = ['address', 'latitude', 'longitude']
    coords_df.to_csv(output_coords_path, index=False)
    print(f"Saved full coordinates to {output_coords_path}")

if __name__ == "__main__":
    DATA_PATH = "data/resale_flat_prices.csv"
    OUTPUT_PATH = "data/hdb_coordinates.csv"
    generate_all_hdb_coordinates(DATA_PATH, OUTPUT_PATH)
