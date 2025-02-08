import requests
import pandas as pd
from datetime import datetime

def fetch_energy_data(start_date, end_date):
    """
    Fetch energy pricing data from the API.
    
    Args:
        start_date (str): Start date in YYYYMMDD format
        end_date (str): End date in YYYYMMDD format
    
    Returns:
        dict: JSON response from the API
    """
    base_url = "https://pge-pe-api.gridx.com/v1/getPricing"
    params = {
        "utility": "PGE",
        "market": "DAM",
        "startdate": start_date,
        "enddate": end_date,
        "ratename": "EV2AS",
        "representativeCircuitId": "024040403",
        "program": "CalFUSE"
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch data: {str(e)}")

def process_pricing_data(data):
    """
    Process the raw JSON data into a pandas DataFrame.
    
    Args:
        data (dict): Raw JSON data from the API
    
    Returns:
        pandas.DataFrame: Processed data
    """
    try:
        # Extract pricing data
        pricing_data = []
        for item in data.get('data', []):
            datetime_str = item.get('datetime')
            price = item.get('price')
            
            if datetime_str and price is not None:
                # Convert datetime string to datetime object
                dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
                pricing_data.append({
                    'datetime': dt,
                    'price': float(price)
                })
        
        # Create DataFrame
        df = pd.DataFrame(pricing_data)
        
        # Sort by datetime
        df = df.sort_values('datetime')
        
        return df
    
    except Exception as e:
        raise Exception(f"Failed to process data: {str(e)}")
