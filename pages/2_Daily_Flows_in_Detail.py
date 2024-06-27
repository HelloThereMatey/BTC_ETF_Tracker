import os
import sys
import streamlit as st
st.set_page_config(layout="wide", page_icon=":bird:")

import altair as alt
import pandas as pd

fdel = os.path.sep
wd = os.path.dirname(__file__)  ## This gets the working directory which is the folder where you have placed this .py file. 
parent = os.path.dirname(wd)
sys.path.append(wd+fdel+"backend")
from backend import btc_etfs, charts

#Get data on daily flows ######
hybrid_df, last_block_day = btc_etfs.get_hybrid_flows_table()
hybrid_df.index.rename('Date', inplace=True)
hybrid_df /= 1000000  # Convert to millions of USD

net_flow = hybrid_df.sum(axis=1).rename('Net flow total (USD)')
hybrid_flow_table_deet = pd.concat([hybrid_df.copy(), net_flow], axis=1)
index = hybrid_flow_table_deet.index.strftime('%Y-%m-%d')

fig = charts.plotly_bar_sl(hybrid_df, custom_index = index, width = 1200, height = 750, ytitle="Net flow for ETF on date (USD millions)")

################ Streamlit commands below ############################
st.subheader("Daily fund flows for all Spot BTC ETFs (USD)")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Daily fund flows data table (USD)")
st.caption("Data yet to be finalized for dates after: "+last_block_day.strftime('%Y-%m-%d')+". \
                Data for days after this date may be subject to revision.")
st.dataframe(hybrid_flow_table_deet, use_container_width=True)
st.divider()