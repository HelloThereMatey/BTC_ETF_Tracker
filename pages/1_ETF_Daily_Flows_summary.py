# Description: Streamlit app page 1 for visualizing daily flows into and out of U.S Bitcoin spot ETFs.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import streamlit as st
import altair as alt

import backend  #This is my backend file that houses the functions and classes for getting the data and plotting templates etc. 

fdel = os.path.sep
wd = os.path.dirname(__file__)  ## This gets the working directory which is the folder where you have placed this .py file. 
parent = os.path.dirname(wd)

#Get data on daily flows ######
hybrid_df, last_block_day = backend.btc_etfs.get_hybrid_flows_table()
hybrid_df.index.rename('Date', inplace=True)
hybrid_df /= 1000000  # Convert to millions of USD

first_four = hybrid_df.iloc[:, :4]
sum_others = hybrid_df.iloc[:, 4:].sum(axis=1)
short_df = first_four.assign(SumOthers=sum_others).rename(columns={'SumOthers': 'Others'})
net_flow = short_df.sum(axis=1).rename('Net flow total (USD)')
short_df2 = pd.concat([short_df, net_flow], axis=1)
custom_index = short_df.index.strftime('%Y-%m-%d')

cum_flows = hybrid_df.cumsum(axis = 0)

short_df3 = short_df2.copy().set_index(custom_index, drop = True)
hybrid_flow_table_deet = pd.concat([hybrid_df.copy(), net_flow], axis=1)

alt_chart = alt.Chart(short_df).mark_bar().encode(
    x=alt.X('Subcategory:N', axis=alt.Axis(title='')),
    y=alt.Y('Value:Q', axis=alt.Axis(title='Value')),
    color='Subcategory:N',
    column='Category:N'
)

################ Streamlit commands below ############################
st.set_page_config(layout="wide", page_icon=":cat:")

#st, space, st  = st.columns([1, 0.05, 1])  # Adjust the middle value to increase or decrease the space
st.title("Daily USD flows into and out of U.S Bitcoin spot ETFs.")
st.caption("Data sources: The Block, Farside Investors.")
st.caption("Data yet to be finalized for dates after: "+last_block_day.strftime('%Y-%m-%d')+". \
                Data for days after this date may be subject to revision. This applies to all charts here.")
st.caption("Recommended: Minimize the page choice bar at left to best view charts with full screen.")
st.divider()

fig = backend.charts.plotly_bar_sl(short_df, custom_index, width = 800, height = 650, ytitle="Net flow for Spot ETF on date (USD millions)")

# Display the figure in the Streamlit app
st.caption("Plotly grouped bar chart. Slide bar at bottom to change date range.")
st.plotly_chart(fig, use_container_width=True)
st.divider()
st.caption("Altair stacked bar chart showing the same flow data.")
st.bar_chart(short_df2, use_container_width=True)
st.divider()

st.subheader("Daily net flow (USD)")
st.bar_chart(net_flow,use_container_width=True)
st.divider()
st.subheader("Cumulative flows since inception (USD)")
st.bar_chart(cum_flows, use_container_width=True)
st.divider()

