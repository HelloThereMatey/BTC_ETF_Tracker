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

logo = plt.imread(parent+fdel+"Macro_Bootlegger.jpg")

#Get data on daily flows ######
hybrid_df, last_block_day = backend.btc_etfs.get_hybrid_flows_table()
hybrid_df.index.rename('Date', inplace=True)

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

col1, space, col2  = st.columns([1, 0.05, 1])  # Adjust the middle value to increase or decrease the space
col1.title("Bitcoin: U.S Spot ETF Tracker")
col1.subheader("By the Macro Bootlegger.")
col1.caption("Data sources: The Block, Farside Investors.")
col2.image(logo, use_column_width=False, width = 150)
col2.caption("Follow me on: Twitter/𝕏: @Tech_Pleb, Github: @HelloThereMatey")
col2.caption("Reccomended: Minimize the page choice bar at left to best view charts.")
col2.divider()

fig = backend.charts.plotly_bar_sl(short_df, custom_index, width = 800, height = 600)

# Display the figure in the Streamlit app
col1.subheader("Daily USD flows into and out of U.S Bitcoin spot ETFs.")
col1.caption("Plotly grouped bar chart. Slide bar at bottom to change date range.")
col1.plotly_chart(fig, use_container_width=True)
col1.divider()
col1.caption("Altair stacked bar chart showing the same flow data.")
col1.bar_chart(short_df2, use_container_width=True)
col1.divider()

col2.subheader("Daily net flow (USD)")
col2.caption("Data yet to be finalized for dates after: "+last_block_day.strftime('%Y-%m-%d')+". \
                Data for days after this date may be subject to revision. This applies to all charts here.")
col2.bar_chart(net_flow,use_container_width=True)
col2.divider()
col2.subheader("Cumulative flows since inception (USD)")
col2.bar_chart(cum_flows, use_container_width=True)
col2.divider()
col2.subheader("Daily fund flows data table (USD)")
col2.dataframe(hybrid_flow_table_deet, use_container_width=True)
col2.divider()


