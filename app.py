
# Imports
import numpy as np
import pandas as pd 
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go  
import plotly.subplots as sp 

from utils.bmrs_data import get_bmrs_data



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
    
    
    
# Run the main function
if __name__ == "__main__":
    main()