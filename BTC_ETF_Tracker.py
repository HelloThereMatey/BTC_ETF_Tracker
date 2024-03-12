import pandas as pd
import streamlit as st
import backend
import os
import matplotlib.pyplot as plt

fdel = os.path.sep
wd = os.path.dirname(__file__)  ## This gets the working directory which is the folder where you have placed this .py file. 
parent = os.path.dirname(wd)

st.set_page_config(page_icon=":bird:")

logo = plt.imread(wd+fdel+"Macro_Bootlegger.jpg")
menu_items = {"Get help": "www.suckle_adingaling.com", "Report a bug": "www.suckle_adingaling.com", "About": "www.suckle_adingaling.com"}
page_items = {"Flows_Dollars":"ETF daily in/outflow (USD)", "Flows_BTC":"ETF daily in/outflow (BTC)", "AUM_USD":"ETF AUM (USD)",
              "AUM_BTC":"ETF AUM (BTC)"}

st.title("Bitcoin: U.S Spot ETF Tracker")
st.subheader("By the Macro Bootlegger.")
st.caption("Data sources: The Block, Farside Investors.")
st.image(logo, use_column_width=False, width = 150)
st.caption("Follow me on: Twitter/𝕏: @Tech_Pleb")
st.caption("Github: @HelloThereMatey")
st.divider()

import plotly.graph_objects as go
import pandas as pd
