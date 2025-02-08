import requests
import pandas as pd
from datetime import datetime
import json

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
        # Debug print to see the structure of the data
        print("Raw API Response:", json.dumps(data, indent=2))

        # Extract pricing data
        pricing_data = []

        # Check if data is in the expected format
        if not isinstance(data, dict):
            raise ValueError("API response is not in the expected format")

        # Get the data array, which might be nested
        data_array = data.get('data', [])
        if not data_array:
            raise ValueError("No pricing data found in the API response")

        for item in data_array:
            # Handle different possible datetime field names
            datetime_str = None
            for field in ['datetime', 'date', 'timestamp']:
                if field in item:
                    datetime_str = item[field]
                    break

            price = item.get('price')

            if datetime_str and price is not None:
                try:
                    # Try different datetime formats
                    dt = None
                    formats_to_try = [
                        '%Y-%m-%d %H:%M:%S',
                        '%Y-%m-%dT%H:%M:%S',
                        '%Y%m%d%H%M%S'
                    ]

                    for fmt in formats_to_try:
                        try:
                            dt = datetime.strptime(datetime_str, fmt)
                            break
                        except ValueError:
                            continue

                    if dt is None:
                        raise ValueError(f"Could not parse datetime: {datetime_str}")

                    pricing_data.append({
                        'datetime': dt,
                        'price': float(price)
                    })
                except ValueError as e:
                    print(f"Warning: Skipping record due to datetime parsing error: {str(e)}")
                    continue

        if not pricing_data:
            raise ValueError("No valid pricing data records found after processing")

        # Create DataFrame
        df = pd.DataFrame(pricing_data)

        # Sort by datetime
        df = df.sort_values('datetime')

        return df

    except Exception as e:
        print(f"Error processing data: {str(e)}")
        print("Data received:", data)
        raise Exception(f"Failed to process data: {str(e)}")