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
hybrid_flow_table_deet = hybrid_flow_table_deet[::-1]  # Invert the order of the rows
index = hybrid_flow_table_deet.index.strftime('%Y-%m-%d')
hybrid_flow_table_deet = hybrid_flow_table_deet.reset_index(drop=True)
hybrid_flow_table_deet = hybrid_flow_table_deet.set_index(index)
#hybrid_df custom_index = index

#hybrid_df = hybrid_df[::-1]  #Invert index so that the most recent date is at the top
fig = charts.plotly_bar_sl(hybrid_flow_table_deet, width = 1200, height = 750, ytitle="Net flow for ETF on date (USD millions)")

################ Streamlit commands below ############################
st.subheader("Daily fund flows for all Spot BTC ETFs (USD)")
st.caption("If you cannot see any bars it is because the date range is too wide which has made the bars too thin to see. Use the date slider to view\
            a smaller sub-range and then move that range around to view all the data.")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Daily fund flows data table (USD)")
st.caption("Data yet to be finalized for dates after: "+last_block_day.strftime('%Y-%m-%d')+". \
                Data for days after this date may be subject to revision.")
st.dataframe(hybrid_flow_table_deet, use_container_width=True)
st.divider()