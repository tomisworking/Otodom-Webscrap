import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import time
import random

def get_location_name(location_data):
    """Helper function to extract district name from nested location dictionary"""
    try:
        # Example structure: location['reverseGeocoding']['locations']
        # We look for the 'district' level or return the entire object
        if isinstance(location_data, dict):
            reverse_geo = location_data.get('reverseGeocoding', {})
            locations = reverse_geo.get('locations', [])
            districts = [loc.get('fullName') for loc in locations if loc.get('locationLevel') == 'district']
            if districts:
                return districts[0]
            # Fallback to anything available
            if locations:
                return locations[-1].get('fullName')
    except Exception as e:
        pass
    return str(location_data)

def extract_price(price_data):
    """Returns the raw numerical value of the price"""
    try:
        if isinstance(price_data, dict):
            return price_data.get('value')
        return price_data
    except:
        return None

def load_options(filepath="options.json"):
    """Loads scraping options from a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File {filepath} not found. Using default options.")
        return {
            "transaction": "wynajem",
            "estate": "mieszkanie",
            "region": "dolnoslaskie",
            "city": "wroclaw",
            "district": "",
            "pages": 3,
            "min_delay": 1.5,
            "max_delay": 3.5,
            "output_file": "wynajem_wroclaw.csv"
        }

def build_url(opts):
    """Builds base URL for Otodom based on options."""
    # Base pattern is usually: /pl/wyniki/{transaction}/{estate}/{region}/{city}/{city}/{city}/{district}
    # However, for main city search it is just /city/city/city
    city_lower = opts.get("city", "wroclaw").lower()
    base = f"https://www.otodom.pl/pl/wyniki/{opts.get('transaction', 'wynajem')}/{opts.get('estate', 'mieszkanie')}/{opts.get('region', 'dolnoslaskie')}/{city_lower}/{city_lower}/{city_lower}"
    
    district = opts.get("district", "")
    if district:
        base += f"/{district.lower()}"
        
    return base

def scrape_otodom(options_file="options.json"):
    opts = load_options(options_file)
    pages = opts.get("pages", 3)
    base_url = build_url(opts)
    output_file = opts.get("output_file", "scraped_data.csv")
    min_delay = opts.get("min_delay", 1.5)
    max_delay = opts.get("max_delay", 3.5)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    
    all_data = []

    print(f"Target URL: {base_url}")
    print(f"Goal: {pages} pages. Will save to: {output_file}")

    for page in range(1, pages + 1):
        print(f"Fetching page {page}/{pages}...")
        
        # If page = 1 we use base_url, otherwise append ?page=N parameter
        # Need to handle existing query parameters if any, but since we build from scratch, it's safe.
        url = f"{base_url}?viewType=listing&page={page}" if page > 1 else base_url
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Error! Status code: {response.status_code}")
            break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        next_data_script = soup.find('script', id='__NEXT_DATA__')
        
        if not next_data_script:
            print("Could not find __NEXT_DATA__ on this page. Stopping.")
            break
            
        try:
            data = json.loads(next_data_script.string)
            # Otodom data structure
            items = data.get('props', {}).get('pageProps', {}).get('data', {}).get('searchAds', {}).get('items', [])
            
            if not items:
                print("No properties found on this page, stopping.")
                break
                
            for item in items:
                row = {
                    'id': item.get('id'),
                    'title': item.get('title'),
                    'total_price': extract_price(item.get('totalPrice')),
                    'rent_price': extract_price(item.get('rentPrice')),
                    'price_per_sqm': extract_price(item.get('pricePerSquareMeter')),
                    'area': item.get('areaInSquareMeters'),
                    'rooms': item.get('roomsNumber'),
                    'floor': item.get('floorNumber'),
                    'location': get_location_name(item.get('location'))
                }
                all_data.append(row)
                
            print(f" -> Successfully scraped {len(items)} offers from page {page}.")
            
            # Pause to avoid overloading the server and getting banned
            time.sleep(random.uniform(min_delay, max_delay))
            
        except Exception as e:
            print(f"Error parsing JSON on page {page}: {e}")
            break
            
    # Save everything to a CSV using pandas
    if all_data:
        df = pd.DataFrame(all_data)
        # Remove potential duplicates based on ID
        df = df.drop_duplicates(subset=['id'], keep='first')
        
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\nFinished! Saved {len(df)} unique offers to {output_file}.")
    else:
        print("No data to save.")

if __name__ == "__main__":
    scrape_otodom("options.json")
