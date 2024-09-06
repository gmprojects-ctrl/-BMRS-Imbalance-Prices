
# Imports
import numpy as np
import pandas as pd 
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go   

from utils.bmrs_data import get_bmrs_data


# Main function
def main():
    st.title("BMRS Data")
    
    # Enter the date
    date = st.date_input("Enter the start date",format="DD/MM/YYYY").strftime("%Y-%m-%d")
    
    
    # Get the data
    data = get_bmrs_data(date)
    
    # Write the data
    st.write(data)
    
# Run the main function
if __name__ == "__main__":
    main()