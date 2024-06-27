import pandas as pd
import streamlit as st
import os
import sys
import matplotlib.pyplot as plt

fdel = os.path.sep
wd = os.path.dirname(__file__)  ## This gets the working directory which is the folder where you have placed this .py file. 
parent = os.path.dirname(wd)

st.set_page_config(page_icon=":bird:")

logo = plt.imread(wd+fdel+"Macro_Bootlegger.jpg")
bitty = plt.imread(wd+fdel+"bitcoin.jpg")
menu_items = {"Get help": "www.suckle_adingaling.com", "Report a bug": "www.suckle_adingaling.com", "About": "www.suckle_adingaling.com"}
page_items = {"Flows_Dollars":"ETF daily in/outflow (USD)", "Flows_BTC":"ETF daily in/outflow (BTC)", "AUM_USD":"ETF AUM (USD)",
              "AUM_BTC":"ETF AUM (BTC)"}

st.title("Bitcoin: U.S Spot ETF Tracker")
st.image(bitty, use_column_width=False, width = 100)
st.subheader("By the Macro Bootlegger.")
block_url = "https://www.theblock.co/data/crypto-markets/bitcoin-etf"
farside_url = "https://farside.co.uk/?p=997"
st.markdown("Data sources: The Block: [link](%s)" % block_url)
st.markdown("Farside Investors: [link](%s)" % farside_url)
st.caption("Thank you very much sources, have a look at those sources. I like my charts better though.")
st.image(logo, use_column_width=False, width = 250)
st.caption("Follow me on: Twitter/𝕏: @Tech_Pleb")
st.caption("Github: @HelloThereMatey")
st.caption("Chuck me some sats if you would kind ser: sixhallway54@walletofsatoshi.com")
st.divider()