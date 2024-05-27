import streamlit as st
import pandas as pd
import os
import sys
import altair as alt

st.set_page_config(layout = "wide", page_icon=":dog:")

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

st.subheader("ETF AUM Historical data(USD), last update: "+last_update)
st.altair_chart(charts.altair_line(aum_dollars, right_columns = ['GBTC'], axis_title = "Billions of U.S $").interactive(), use_container_width=True)
st.caption("GBTC plotted vs right axis. All other funds plotted vs left axis.")

st.divider()
st.subheader("Latest AUM distribution.")
st.caption("Pie chart below shows the current distribution of AUM in USD across the Spot ETFs.")
st.plotly_chart(pie_fig, use_container_width=True)

st.divider()
st.subheader("BTC holdings of the Spot ETF funds.")
st.caption("This shows the BTC holdings of the ETF funds. GBTC plotted vs right axis. All other funds plotted vs left axis.")
st.altair_chart(charts.altair_line(btcholdings, right_columns = ['GBTC'], axis_title = "BTC").interactive(), use_container_width=True)
st.divider()