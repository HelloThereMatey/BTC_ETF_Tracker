import streamlit as st
import altair as alt
import backend as bk
import pandas as pd
import os

st.set_page_config(layout = "wide", page_icon=":dog:")

fdel = os.path.sep
wd = os.path.dirname(__file__)  ## This gets the working directory which is the folder where you have placed this .py file. 
parent = os.path.dirname(wd)

######### GET AUM DATA ########################
aum_dollars = bk.btc_etfs.btc_etf_data(metric="etf_aum_daily").df
aum = bk.btc_etfs.btc_etf_data(metric="btc_etf_aum", export_response=True)
latest_aum = aum.df
last_update = aum.last_update.strftime('%Y-%m-%d')

pie_fig = bk.btc_etfs.plotly_pie(latest_aum, title = "Latest AUM Distribution (%), Updated: "+last_update)

col1, col2  = st.columns(2)
col1.title("Bitcoin: U.S Spot ETF's, Assets under management - AUM (USD)")

col1.divider()
col1.subheader("ETF AUM Historical data(USD), last update: "+last_update)
col1.line_chart(aum_dollars, use_container_width=True)

col2.divider()
col2.subheader("Latest AUM distribution.")
col2.plotly_chart(pie_fig, use_container_width=True)