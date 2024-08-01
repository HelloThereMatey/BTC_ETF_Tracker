# Description: Streamlit app page 1 for visualizing daily flows into and out of U.S Bitcoin spot ETFs.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import streamlit as st
st.set_page_config(layout="wide", page_icon=":cat:")       #Must be up top........

import altair as alt

fdel = os.path.sep
wd = os.path.dirname(__file__)  ## This gets the working directory which is the folder where you have placed this .py file. 
parent = os.path.dirname(wd)
sys.path.append(wd+fdel+"backend")
from backend import btc_etfs, charts

#Get data on daily flows ######
hybrid_df, last_block_day = btc_etfs.get_hybrid_flows_table()
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

#st, space, st  = st.columns([1, 0.05, 1])  # Adjust the middle value to increase or decrease the space
st.title("Daily USD flows into and out of U.S Bitcoin spot ETFs.")
st.caption("Data sources: The Block, Farside Investors.")
st.caption("Data yet to be finalized for dates after: "+last_block_day.strftime('%Y-%m-%d')+". \
                Data for days after this date may be subject to revision. This applies to all charts here.")
st.caption("Recommended: Minimize the page choice bar at left to best view charts with full screen.")
st.divider()

fig = charts.plotly_bar_sl(short_df, custom_index, width = 800, height = 650, ytitle="ETF net flow (USD millions)")

# Display the figure in the Streamlit app
st.caption("Plotly grouped bar chart. Slide bar at bottom to change date range. Bar show the net flow (flows in - flows out) for specific ETF on that date.")
st.plotly_chart(fig, use_container_width=True)
st.divider()
st.caption("Altair stacked bar chart showing the same flow data.")
st.bar_chart(short_df2, use_container_width=True)
st.divider()

######################## DAILY FLOWS FOR EACH ETF ##################################################################
st.subheader("Daily net flow (USD)")

# Calculate the moving average
net_flow.index.rename("Date", inplace=True)
net_flow2 = net_flow.reset_index()
window = 20
net_flow2[str(window) + "_MA"] = net_flow2['Net flow total (USD)'].rolling(window=window).mean()

# Create the bar chart with tooltips
bar_chart = alt.Chart(net_flow2).mark_bar(opacity=0.8).encode(
    x=alt.X('Date:T', axis=alt.Axis(title='Date')),
    y=alt.Y('Net flow total (USD):Q', axis=alt.Axis(title='USD (millions)')),
    color=alt.value('skyblue'),
    tooltip=['Date:T', 'Net flow total (USD):Q']
).properties(
    title="Aggregate daily net Flow of all U.S spot ETF's with a 20-day (1 month) Moving Average"
).interactive()

# Create the line chart with tooltips
line_chart = alt.Chart(net_flow2).mark_line().encode(
    x=alt.X('Date:T', axis=alt.Axis(title='Date')),
    y=alt.Y(str(window) + "_MA:Q", axis=alt.Axis(title='USD (millions)')),
    color=alt.value('red'),
    tooltip=['Date:T', str(window) + "_MA:Q"]
).properties(
    title="Aggregate daily net Flow of all U.S spot ETF's with a 20-day (1 month) Moving Average"
).interactive()

# Combine the charts
combined_chart = alt.layer(bar_chart, line_chart).resolve_scale(
    y='shared'
)

# Display the interactive chart in Streamlit
st.altair_chart(combined_chart, use_container_width=True)
st.caption("This is the sum of all ETF flows for each day. Positive values indicate more money flowed in than out. \
           Red line is a 20-day moving average. ")
st.divider()

cum_flows = short_df.cumsum()

####### Cumulative flows ###################################################################
fig2 = charts.plotly_bar_sl(cum_flows, custom_index, width = 800, height = 650, ytitle="Cumulative flows (USD millions)")
st.subheader("Cumulative flows since inception (USD)")
st.plotly_chart(fig2, use_container_width=True)
st.caption("This chart shows the cumulative net flow for that ETF since the inception. Does not consider the AUM & price changes in the underlying asset.")
st.divider()
st.subheader("Net cumulative flows since inception (USD)")
st.bar_chart(net_flow.cumsum(),use_container_width=True)
st.caption("This chart shows the cumulative net flow for all ETFs since the inception.")
st.divider()

