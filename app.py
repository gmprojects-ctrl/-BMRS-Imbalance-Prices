
# Imports
import numpy as np
import pandas as pd 
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go  
import plotly.subplots as sp 
from statsmodels.tsa.stattools import pacf
from statsmodels.tsa.stattools import acf
from statsmodels.tsa.stattools import adfuller
from scipy.stats import normaltest
from sklearn.linear_model import LinearRegression


# Custom imports
from utils.bmrs_data import get_bmrs_data
from utils.bmrs_data import get_bmrs_data_range

# Logging
import logging


# APP constants
DATE_FORMAT = "%Y-%m-%d"
DATA100_LOC = "./data.feather"


# App logging
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
FILE_HANDLER = logging.FileHandler("app.log")
FILE_HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(FILE_HANDLER)
STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.info("App started")


# App functions
@st.cache_data()
def app_load(path:str = DATA100_LOC) -> pd.DataFrame:
    '''
    Title: app_load
    Description: This function loads the data
    Arguments:
        path: str - The path to the data
    Returns:
        pd.DataFrame - The data
    '''
    
    # Try to load the data
    try:
        data = pd.read_feather(path)
        return data
    except Exception as e:
        # If there is an error, return an empty dataframe
        LOGGER.error("Error loading data: %s",e)
        raise Exception("Error loading data")
def app_save(data:pd.DataFrame,path:str = DATA100_LOC) -> None:
    '''
    Title: app_save
    Description: This function saves the data
    Arguments:
        - data: pd.DataFrame - The data to save
    Returns:
        - None    
    '''
    # Try to save the data
    try:
        data.to_feather(path)
    except Exception as e:
        # If there is an error, log the error
        LOGGER.error("Error saving data: %s",e)
        raise Exception("Error saving data")


# Main function
def main():
    # Ensure the page is wide 
    st.set_page_config(layout="wide")
   
    # Set the title
    st.title("BMRS Data")
    
    # Enter the date
    date = st.date_input("Enter the start date",format="DD/MM/YYYY").strftime("%Y-%m-%d")
    
    
    # Get the data
    data = get_bmrs_data(date)
    
    # If the data is empty raise an error
    if data.empty:
        raise ValueError("No data found")
    
    # Add absolute net imbalance volume
    data['ABSnetImbalanceVolume'] = np.abs(data['netImbalanceVolume'])

    
    # Vectorised pandas application
    def cost_create(row: pd.Series) -> np.float64:
        '''
        Title: cost_create
        Description: This function creates the costs based on the net imbalance volume abs and the system buy and sell price
        Arguments:
            - row: pd.Series - The row of the data
        Returns:   
            - np.float64 - The costs
        '''
        # Check net imbalance volume
        if row['netImbalanceVolume'] > 0:
            # If netImbalanceVolume is greater than 0, you have to sell power at the buy price
            return row['netImbalanceVolume'] * row['systemBuyPrice']
        
        if row['netImbalanceVolume'] < 0:
            # If netImbalanceVolume is less than 0, you have to buy power at the sell price
            return np.abs(row['netImbalanceVolume']) * row['systemSellPrice']
        
        # If netImbalanceVolume is 0, you don't have to do anything
        return 0
    
    # Apply the vectoried function
    data['Costs'] = data.apply(cost_create,axis=1)  
    
    # Create hourly balances
    hourly_data = data[['ABSnetImbalanceVolume','Costs']].groupby(by=[data['startTime'].dt.hour]).sum().reset_index()
   
    
    # Sort values of hourly data by ABSnetImbalanceVolume
    hourly_data = hourly_data.sort_values(by=['ABSnetImbalanceVolume'])
   
 
    
    # Get the hightest hour
    highest_hour_volume = hourly_data.iloc[-1,:]['startTime']
    
    # Get the most expensive hour
    hourly_data = hourly_data.sort_values(by=["Costs"])
    highest_hour_cost = hourly_data.iloc[-1,:]['startTime']
    cost_highest_hour = hourly_data.iloc[-1,:]['Costs']
    
    
    
    
    
    # Peak min mean max buy price
    peak_buy_price = data['systemBuyPrice'].max()
    peak_buy_price_time = pd.to_datetime(data[data['systemBuyPrice'] == peak_buy_price]['startTime'].values[0]).strftime("%Y-%m-%d %H:%M:%S")
    
    min_buy_price = data['systemBuyPrice'].min()
    min_buy_price_time = pd.to_datetime(data[data['systemBuyPrice'] == min_buy_price]['startTime'].values[0]).strftime("%Y-%m-%d %H:%M:%S")
    
    mean_buy_price = data['systemBuyPrice'].mean()
    
    # Peak min mean max sell price
    peak_sell_price = data['systemSellPrice'].max()
    peak_sell_price_time = pd.to_datetime(data[data['systemSellPrice'] == peak_sell_price]['startTime'].values[0]).strftime("%Y-%m-%d %H:%M:%S")
    
    min_sell_price = data['systemSellPrice'].min()
    min_sell_price_time = pd.to_datetime(data[data['systemSellPrice'] == min_sell_price]['startTime'].values[0]).strftime("%Y-%m-%d %H:%M:%S")  
    mean_sell_price = data['systemSellPrice'].mean()
    
    # Peak min mean max imbalance volume
    peak_imbalance_volume = data['netImbalanceVolume'].max()
    peak_imbalance_volume_time = pd.to_datetime(data[data['netImbalanceVolume'] == peak_imbalance_volume]['startTime'].values[0]).strftime("%Y-%m-%d %H:%M:%S")
    
    min_imbalance_volume = data['netImbalanceVolume'].min()
    min_imbalance_volume_time = pd.to_datetime(data[data['netImbalanceVolume'] == min_imbalance_volume]['startTime'].values[0]).strftime("%Y-%m-%d %H:%M:%S") 
    
    mean_imbalance_volume = data['netImbalanceVolume'].mean()
    

    
    # Get total daily costs
    total_daily_costs =  data['Costs'].sum()
    
    # Get the total daily net imbalance volume
    total_daily_volume = data['ABSnetImbalanceVolume'].sum()
    
    # Get the unit rate
    unit_rate = total_daily_costs / total_daily_volume
    
    # Divide the page
    st.divider()
    
    # Write the total daily costs
    st.write(f"The total daily costs are: {total_daily_costs:,.2f}")
    
    # Write the total daily volume
    st.write(f"The unit rate is: {unit_rate:.2f}")
    
    # Write the hour with the highest imbalance volume
    st.write(f"The hour with the highest imbalance volume is: {int(highest_hour_volume):02}:00")
    
    # Write the hour with the highest costs
    st.write(f"The hour with the highest costs is: {int(highest_hour_cost):02}:00 with costs of {cost_highest_hour:,.2f}")
    
    # Divide the page
    tabs = st.tabs(["Buy Price","Sell Price","Imbalance Volume"])
   
    # Buy price tab
    with tabs[0]:
        # Write the peak buy price min buy price and mean buy price
        st.write(f"The peak buy price is: {peak_buy_price:.2f} at {peak_buy_price_time}")
        st.write(f"The min buy price is: {min_buy_price:.2f} at {min_buy_price_time}")
        st.write(f"The mean buy price is: {mean_buy_price:.2f}")
    
    
    # Sell price tab
    with tabs[1]:
        # Write the peak sell price min sell price and mean sell price
        st.write(f"The peak sell price is: {peak_sell_price:.2f} at {peak_sell_price_time}")
        st.write(f"The min sell price is: {min_sell_price:.2f} at {min_sell_price_time}")
        st.write(f"The mean sell price is: {mean_sell_price:.2f}")
    
    # Imbalance volume tab
    with tabs[2]:
        # Write the peak imbalance volume min imbalance volume and mean imbalance volume
        st.write(f"The peak imbalance volume is: {peak_imbalance_volume:.2f} at {peak_imbalance_volume_time}")
        st.write(f"The min imbalance volume is: {min_imbalance_volume:.2f} at {min_imbalance_volume_time}")
        st.write(f"The mean imbalance volume is: {mean_imbalance_volume:.2f}")
    
    # Divide the page
    st.divider()
        
    # Write the data
    st.write(data)
  
    # Add conditional formatting colours to net imbalance volume
    data['color'] = np.where(data['netImbalanceVolume'] >= 0, 'green', 'red')
  
    # Create a plot
    fig = sp.make_subplots(specs=[[{"secondary_y": True}]])
    # Add the net imbalance volume bar chart
    fig.add_trace(go.Bar(x=data['startTime'], y=data['netImbalanceVolume'], name="Net Imbalance Volume", marker={'color': data['color']}))
    # Add the system sell price line chart
    fig.add_trace(go.Scatter(x=data['startTime'], y=data['systemSellPrice'], mode='lines', name="System Sell Price", marker={'color': 'orange'}), secondary_y=True)
    # Add the system buy price line chart
    fig.add_trace(go.Scatter(x=data['startTime'], y=data['systemBuyPrice'], mode='lines', name="System Buy Price", marker={'color': 'blue'}), secondary_y=True)
    
    # Set the y-axis title
    fig.update_yaxes(title_text="Net Imbalance Volume", secondary_y=False)
    # Set the secondary y-axis title
    fig.update_yaxes(title_text="Price", secondary_y=True)
    

    # Add the layout
    fig.update_layout(title="Net Imbalance Volume, System Sell Price and System Buy Price", xaxis_title="Time", yaxis_title="Value")
    
    
    # Set font size for the ticks on the x-axis and y-axiss
    fig.update_layout(yaxis=dict(tickfont=dict(size=18, color='black')), xaxis=dict(tickfont=dict(size=18, color='black')))
    fig.update_layout(yaxis2=dict(tickfont=dict(size=18, color='black')))

    # Update the title font size for the axis
    fig.update_layout(yaxis=dict(title_font=dict(size=18, color='black')))
    fig.update_layout(xaxis=dict(title_font=dict(size=18, color='black')))
    fig.update_layout(yaxis2=dict(title_font=dict(size=18, color='black')))
    
    # Update the legend font size
    fig.update_layout(legend=dict(font=dict(size=18, color='black')))
    
    # Show the plot
    st.plotly_chart(fig)
    
    with st.expander("Sell Price Model of past 100 days"):
        # Markdown to explain what I'm doing
        st.markdown("""
                    Modelling SystemSell Price using an autoregressive model (in this case an $AR(1)$ model) for the past 100 days.
                    
                    """)
        
        
        # Get the current date
        current_date = pd.to_datetime(date)
        
        # Subtract 365 days
        start_date = current_date - pd.Timedelta(days=100)
        
        # Convert to string
        start_date = start_date.strftime("%Y-%m-%d")
        current_date = current_date.strftime("%Y-%m-%d")
        
        
        # Create a load button
        load_button = st.button("Load data")
        
        # Try to load the data
        data100 = app_load()[['startTime','systemSellPrice']]
        LOGGER.info("Data loaded")
        
        
        # If the button is clicked
        if load_button:
            # Load the data
            data100 = get_bmrs_data_range(start_date,current_date)
            
            # Save the data
            app_save(data100)
            LOGGER.info("Data loaded and saved")
        
        # If the data is empty raise an error
        if data100.empty:
            LOGGER.error("No data found")
            raise ValueError("No data found")
        
        # Write the data
        st.write(data100)
        
        # Plot the system sell price against time
        st.plotly_chart(px.line(data100,x='startTime',y='systemSellPrice',title="System Sell Price vs Time"))
        
       
    
        # Run adfuller test
        adf_test = adfuller(data100['systemSellPrice'])
        
        # Run acf
        acf_vals = acf(data100['systemSellPrice'])
        
        # Run pacf
        pacf_vals = pacf(data100['systemSellPrice'])

        # Write the p-value
        st.write(f"The p-value for the Dickey-Fueller test is: {adf_test[1]}")
    
    
        # Plot the acf and pacf
        fig = go.Figure()
        fig.add_bar(x=np.arange(len(acf_vals)),y=acf_vals,name="ACF")
        fig.add_bar(x=np.arange(len(pacf_vals)),y=pacf_vals,name="PACF")
        # Set the title
        fig.update_layout(title="ACF and PACF of System Sell Price")
        
        # Show the plot
        st.plotly_chart(fig)  
        
        # Create the lagged features of -1
        data100['lag1'] = data100['systemSellPrice'].shift(1)
        
        # Drop the na values
        data100 = data100.dropna()
        
        
        # Create a 80/20 split
        split = int(0.8 * len(data100))
        
        # Create the training data
        X_train = data100[['lag1']].iloc[:split]
        y_train = data100['systemSellPrice'].iloc[:split]
        
        # Create the testing data
        X_test = data100[['lag1']].iloc[split:]
        y_test = data100['systemSellPrice'].iloc[split:]
        
        # Create the model
        model = LinearRegression()
        model.fit(X_train,y_train)
        
        # Get the predictions
        preds_train = model.predict(X_train)    
        
        # Get the residuals
        residuals = y_train - preds_train
        
        # Normal test on residuals
        normal_p = normaltest(residuals)[1]
        
        # Get the predictions
        pred_test = model.predict(X_test)
        
        # Get the error
        error = y_test - pred_test
        
        # Get the mean squared error
        mse = np.mean(error**2)
        
        
        # Plot the training data
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data100['startTime'].iloc[:split],y=y_train,name="Actual"))
        fig.add_trace(go.Scatter(x=data100['startTime'].iloc[:split],y=preds_train,name="Predicted",line=dict(color='red')))
        fig.update_layout(title="Actual vs Predicted System Sell Price on Training Data")
        st.plotly_chart(fig)
        
    
        
        
        
        
        # Plot the residuals as a histogram
        st.plotly_chart(px.histogram(residuals,x=residuals.index,y=residuals,title="Residuals of Training Histogram"))
        
        # Write a normality test
        st.write(f"The p-value of a normal test done on the residuals results {normal_p:.2E}")    
        
        # Plot the testing data
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data100['startTime'].iloc[split:],y=y_test,name="Actual"))
        fig.add_trace(go.Scatter(x=data100['startTime'].iloc[split:],y=pred_test,name="Predicted",line=dict(color='red')))
        fig.update_layout(title="Actual vs Predicted System Sell Price on Testing Data")
        st.plotly_chart(fig)
        
        
        # Plot the mse
        st.write(f"The mean squared error is: {mse:.2f}")
       
# Run the main function
if __name__ == "__main__":
    main()