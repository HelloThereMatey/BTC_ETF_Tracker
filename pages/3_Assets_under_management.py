import streamlit as st
st.set_page_config(layout = "wide", page_icon=":dog:")

import pandas as pd
import os
import sys
import altair as alt

fdel = os.path.sep
wd = os.path.dirname(__file__)  ## This gets the working directory which is the folder where you have placed this .py file. 
parent = os.path.dirname(wd)

sys.path.append(parent)
from backend import btc_etfs, charts

######### GET AUM DATA ########################
aum_dollars = btc_etfs.scrape_data(metric="etf_aum_daily").df
aum_dollars /= 10e9
aum = btc_etfs.scrape_data(metric="btc_etf_aum", export_response=True)
latest_aum = aum.df
last_update = aum.last_update.strftime('%Y-%m-%d') 
pie_fig = charts.plotly_pie(latest_aum, title = "Latest AUM Distribution (%), Updated: "+last_update)

btcholdings = btc_etfs.scrape_data(metric="btc_holdings").df

# st, st  = st.columns(2)
st.title("Bitcoin: U.S Spot ETF's, Assets under management - AUM (USD)")
st.divider()
st.subheader("Aggregated ETF Holdings across all ETFs listed here")

# Create a box with three segments using columns
col1, col2, col3 = st.columns(3)

# Styling for the metrics box
box_style = """
<style>
    div[data-testid="column"] {
        background-color: #f0f2f6;
        border: 1px solid #e0e0e0;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
    }
</style>
"""
st.markdown(box_style, unsafe_allow_html=True)

# First segment
with col1:
    # You can replace these with your actual metrics
    st.metric(label="Total ETF AUM", 
              value=f"${latest_aum.sum()/(10**9):.2f}B", 
              delta=f"{(latest_aum.sum() - latest_aum.iloc[0:-2].sum())/(10**9):.2f} B")
    st.caption("Total assets under management (USD).")
    st.caption("Green text shows change for latest trading day.")

# Second segment
with col2:
    # Replace with your second metric
    total_btc = btcholdings.iloc[-1].sum()
    st.metric(label="Total BTC Holdings", 
              value=f"{total_btc:,.0f} BTC",
              delta=f"{total_btc - btcholdings.iloc[-2].sum():,.0f}")
    st.caption("Total Bitcoin holdings by all ETFs")
    st.caption("Green text shows change for latest trading day.")

# Third segment - BTC Supply Percentage
with col3:
    # Total circulating supply of BTC (approximately 19.7M as of April 2025)
    # You may want to get this dynamically from an API
    btc_supply = 210000000  # Total supply of Bitcoin  
    supply_percentage = (total_btc / btc_supply) * 100
    
    # If you have historical data, you can calculate the change
    previous_percentage = ((btcholdings.iloc[-2].sum()) / btc_supply) * 100
    percentage_change = supply_percentage - previous_percentage
    
    st.metric(label="% of BTC Supply", 
              value=f"{supply_percentage:.2f}%", 
              delta=f"{percentage_change:.3f}%")
    st.caption("Percentage of total Bitcoin supply held by ETFs")
    st.caption("Green text shows change for latest trading day.")

st.divider()
st.subheader("Latest AUM distribution.")
st.caption("Pie chart below shows the current distribution of AUM in USD across the Spot ETFs.")
st.plotly_chart(pie_fig, use_container_width=True)
st.divider()

st.subheader("ETF AUM Historical data(USD), last update: "+last_update)
st.altair_chart(charts.altair_line(aum_dollars, axis_title = "Billions of U.S $").interactive(), use_container_width=True)

st.divider()
st.subheader("BTC holdings of the Spot ETF funds.")
st.caption("This shows the BTC holdings of the ETF funds.")
st.altair_chart(charts.altair_line(btcholdings, axis_title = "BTC").interactive(), use_container_width=True)