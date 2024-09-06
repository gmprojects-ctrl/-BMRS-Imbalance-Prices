# Libraries
import requests
import numpy as np
import pandas as pd
import json
from typing import Dict
import logging


# CONTANTS
API_LINK = r"https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/system-prices/"
DEFAULT_TIMEOUT = 10

# Create a logger 
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
FILE_HANDLER = logging.FileHandler('bmrs_data.log')
FILE_HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(FILE_HANDLER)
STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(STREAM_HANDLER)
FILE_HANDLER.setLevel(logging.INFO)


# Main request function 
def get_bmrs_raw_data(date:str) -> Dict:
    ''''
    Title: get_bmrs_raw_data
    Description: This function gets the raw data from the BMRS API
    Arguments:
        - date: str - The date to get the data for
    Returns:
        - Dict - The raw data from the API
    '''
    # Create the request
    direct_request = API_LINK + date
    
    # Handle the request
    try:
        response = requests.get(direct_request, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        LOGGER.error(f'HTTP error occurred: {http_err}')
        return {}
    except requests.exceptions.ConnectionError as conn_err:
        LOGGER.error(f'Connection error occurred: {conn_err}')
        return {}
    except requests.exceptions.Timeout as time_err:
        LOGGER.error(f'Timeout error occurred: {time_err}')
        return {}
    
    # Return the response
    return response.json()


# format the data
def format_bmrs_data(data:Dict) -> pd.DataFrame:
    '''
    Title: format_bmrs_data
    Description: This function formats the data from the BMRS API into a pandas dataframe
    Arguments:
        - data: Dict - The raw data from the API
    Returns:
        - pd.DataFrame - The formatted data
    '''
    # Check if the data is empty
    if len(data) == 0:
        LOGGER.error("No data was returned from the API")
        return pd.DataFrame()
    
    # Extract the data
    extracted_data = data["data"]
    
    # Create a filered frame
    filtered_data= [  [entry['startTime'], entry["systemSellPrice"], entry["systemBuyPrice"], entry["netImbalanceVolume"] ]  for entry in extracted_data]         
    
    # Create the dataframe
    output_df = pd.DataFrame(filtered_data, columns=["startTime", "systemSellPrice", "systemBuyPrice", "netImbalanceVolume"])
    
    # Ensure types
    output_df["startTime"] = pd.to_datetime(output_df["startTime"], format="%Y-%m-%dT%H:%M:%SZ")
    output_df["systemSellPrice"] = output_df["systemSellPrice"].astype(np.float64)
    output_df["systemBuyPrice"] = output_df["systemBuyPrice"].astype(np.float64)
    output_df["netImbalanceVolume"] = output_df["netImbalanceVolume"].astype(np.float64)
    
    # Fill na with 0
    output_df = output_df.fillna(0)
    
    # return the frame
    return output_df    


# get the data
def get_bmrs_data(date:str) -> pd.DataFrame:
    
    # Get the raw data
    raw_data = get_bmrs_raw_data(date)
    
    # Format the data
    formatted_data = format_bmrs_data(raw_data)
    
    # Return the data
    return formatted_data

# Get the data between two dates
def get_bmrs_data_range(start_date:str, end_date:str) -> pd.DataFrame:
    '''
    Title: get_bmrs_data_range
    Description: This function gets the data between two dates
    Arguments:
        - start_date: str - The start date
        - end_date: str - The end date
    Returns:
        - pd.DataFrame - The data between the two dates
    '''
    # Create the date range
    date_range = pd.date_range(start=start_date, end=end_date, freq="D").strftime("%Y-%m-%d")
    
    
    # Check if the length is not greater than 100 days
    if len(date_range) > 100:
        LOGGER.error("The date range is too large")
        return pd.DataFrame()
    
    
    # Create a concat object
    concat = []
    
    # Loop through the dates
    for date in date_range:
        # Get the data
        data = get_bmrs_data(date)
        
        # Append to the concat
        concat.append(data)
    
    # Concatenate the data
    output_df = pd.concat(concat)
    
    # Return the data
    return output_df



# Main function
if __name__ == "__main__":
    # Raise error
    raise Exception("This script is not meant to be run directly")