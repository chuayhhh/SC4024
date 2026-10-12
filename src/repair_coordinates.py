import pandas as pd
import requests
import time
from urllib.parse import quote

def fetch_onemap_coord(block, street):
    # Clean address format for OneMap API
    clean_street = str(street).replace('/', ' ').strip()
    clean_block = str(block).strip()
    
    # Query string format: e.g., "406 ANG MO KIO AVE 10"
    query = f"{clean_block} {clean_street}"
    encoded_query = quote(query)
    
    url = f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={encoded_query}&returnGeom=Y&getAddrDetails=Y&pageNum=1"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        res = requests.get(url, headers=headers, timeout=3)
        if res.status_code == 200:
            data = res.json()
            if data.get('found', 0) > 0:
                results = data['results']
                # Pick first result in Singapore
                for r in results:
                    if 'LATITUDE' in r and 'LONGITUDE' in r:
                        return float(r['LATITUDE']), float(r['LONGITUDE'])
    except Exception:
        pass
    return None, None

def repair_missing_coordinates(input_csv, coords_csv):
    df_hdb = pd.read_csv(input_csv)
    df_hdb['address'] = df_hdb['block'].astype(str) + " " + df_hdb['street_name'].astype(str)
    
    # Load existing coordinates
    existing_coords = pd.read_csv(coords_csv)
    
    # Identify addresses that failed (latitude is NaN/None)
    failed_addrs = existing_coords[existing_coords['latitude'].isna()]['address'].tolist()
    print(f"Addresses needing retry/fix: {len(failed_addrs):,}")
    
    coords_map = dict(zip(existing_coords['address'], zip(existing_coords['latitude'], existing_coords['longitude'])))
    
    fixed_count = 0
    for idx, addr in enumerate(failed_addrs):
        sample = df_hdb[df_hdb['address'] == addr].iloc[0]
        block, street = sample['block'], sample['street_name']
        
        lat, lon = fetch_onemap_coord(block, street)
        if lat:
            coords_map[addr] = (lat, lon)
            fixed_count += 1
            
        if (idx + 1) % 500 == 0 or (idx + 1) == len(failed_addrs):
            print(f"Repaired: {idx+1}/{len(failed_addrs)} | Recovered: {fixed_count}")
        time.sleep(0.02)
        
    # Save back
    out_df = pd.DataFrame([
        {'address': k, 'latitude': v[0], 'longitude': v[1]}
        for k, v in coords_map.items()
    ])
    out_df.to_csv(coords_csv, index=False)
    
    valid_total = out_df['latitude'].notna().sum()
    print(f"\n✅ Repair Complete! Total Valid Coordinates: {valid_total}/{len(out_df)} ({valid_total/len(out_df)*100:.1f}%)")

if __name__ == "__main__":
    repair_missing_coordinates("data/resale_flat_prices.csv", "data/hdb_coordinates.csv")
