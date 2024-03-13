import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import re
import matplotlib.pyplot as plt
import json
import os
import plotly.graph_objects as go
import plotly.express as px
import altair as alt
from decimal import Decimal, ROUND_HALF_UP
import datetime
import charts

import streamlit as st

fdel = os.path.sep
wd = os.path.dirname(__file__)  ## This gets the working directory which is the folder where you have placed this .py file. 
parent = os.path.dirname(wd)

def new_request(url: str) -> dict:
    r = requests.get(url)
    print(r.status_code)
    if r.status_code != 200:
        print("Request failed. Status code: ", r.status_code)
        return None
    else:
        resp = r.json()
        return resp

def get_html_save(url: str, save_path: str = wd+fdel+'last_request.html', save: bool = True):
    r = requests.get(url)
    if save:
        with open(save_path, 'w') as wp:
            wp.write(r.text)
    return r.text   

def export_html(html: str, save_path: str = wd+fdel+'last_soup.html'):
    with open(save_path, 'w') as wp:
        wp.write(html)
    return None

def handle_date_range(date_str, year):
    if ' to ' in date_str:
        date_str = date_str.split(' to ')[0]  # return start date
    return date_str + ' ' + str(year) 

# Save JSON object to a file
def json_file_io(filename: str = wd+fdel+'last_request.json', save_load: str = 'load', json_obj = None):
    #Input json_obj only if saving, not loading. 
    
    if save_load == 'save':
        with open(filename, 'w') as f:
            json.dump(json_obj, f)
            print("JSON format data has been saved to the file: ", filename)
            return None
    elif save_load == 'load':
        with open(filename, 'r') as f:
            resp = json.load(f)
            return resp
    else:
        print("Valid values for 'saveload' are 'save' or 'load'. Y'all f**ked urp.")

def html_to_json(content: str, indent=None) -> str:
    soup = BeautifulSoup(content, "html.parser")
    rows = soup.find_all("tr")
    
    headers = {}
    thead = soup.find("thead")
    if thead:
        thead = soup.find_all("th")
        for i in range(len(thead)):
            headers[i] = thead[i].text.strip().lower()
    data = []
    for row in rows:
        cells = row.find_all("td")
        if thead:
            items = {}
            if len(cells) > 0:
                for index in headers:
                    items[headers[index]] = cells[index].text
        else:
            items = []
            for index in cells:
                items.append(index.text.strip())
        if items:
            data.append(items)
    return json.dumps(data, indent=indent)

def combine_etf_datasets(df1: pd.DataFrame, df2: pd.DataFrame):
    if set(df1.columns) != set(df2.columns):
        print("The columns of the two datasets are not the same. Cannot combine them. Pulling out....")
        quit()
    
    df2 = df2.reindex(columns=df1.columns)
    lastday = df1.index[-1]
    to_add = df2.loc[lastday:].drop(lastday, axis = 0)
    hydrid_df = pd.concat([df1, to_add], axis = 0)   

    return hydrid_df

class btc_etf_data(object):
    def __init__(self, source: str = "theblock", metric: str = "etf_flows", export_response: bool = False):
        block_base_url = "https://www.theblock.co/api/charts/chart/crypto-markets/bitcoin-etf/"
        self.etf_urls = {"theblock": {"etf_flows": block_base_url+"spot-bitcoin-etf-flows",
                "etf_aum_daily": block_base_url+"spot-bitcoin-etf-assets-daily",
                "btc_etf_aum": block_base_url+"spot-bitcoin-etf-assets",
                "exGBTC_etf_aum_hist": block_base_url+"spot-bitcoin-etf-aum-ex-gbtc-daily"},
                "farside": {"etf_flows": "https://farside.co.uk/?p=997"}}
        
        self.source = source; self.metric = metric
        self.url = self.etf_urls[source][metric]
        print(f"Requesting data from {source} for {metric}..")
        if self.source == "farside" and self.metric == "etf_flows":
            try:
                self.df = self.get_farside_table()
            except Exception as e:
                print("Data retrieval from Farside Investors site failed. Pulling out... Error message: ", e)
                quit()
        else:    
            self.resp = new_request(self.url)
            if self.resp is not None:
                print("Data successfully retrieved.")
                try:
                    self.df = self.block_json_to_df()
                except Exception as e:
                    print(f"Conversion of json format data to DataFrame failed. Error: {e}. \
                        Returning the raw json format data instead. You can access that through self.resp.")
            else:
                print("Data retrieval failed. Pulling put.....")
                quit()

        if export_response:
            json_file_io(save_load = 'save', json_obj = self.resp, filename = wd+fdel+self.metric+"_"+self.source+'.json')     
        try:    
            self.last_update = pd.to_datetime(self.resp["chart"]["jsonFile"]["UpdatedAt"], unit = 's')
        except:
            pass    

    def block_json_to_df(self, key1: str = 'chart', key2: str = 'jsonFile', key3: str = 'Series')-> pd.DataFrame:
        series = dict(self.resp[key1][key2][key3])
        print("Dataset: ", self.resp[key1][key2]["Description"], "\nStart: ", pd.to_datetime(self.resp[key1][key2]["Start"], unit='s'),\
            "\nUpdated last: ", pd.to_datetime(self.resp[key1][key2]["UpdatedAt"], unit='s'))

        i = 0; output_df = pd.Series()
        for ticker in series.keys():
            data_series = pd.json_normalize(series[ticker]['Data'])
            if self.metric == "btc_etf_aum":
                output_df = data_series if i == 0 else pd.concat([output_df, data_series], axis=0)

            else:
                index = pd.to_datetime(data_series['Timestamp'], unit='s')
                data_series = data_series.set_index(index, drop = True).drop('Timestamp', axis = 1).squeeze().rename(ticker) 
                output_df = data_series if i == 0 else pd.concat([output_df, data_series], axis = 1)
            i += 1

        if self.metric == "btc_etf_aum":
            return output_df.set_index('Name', drop = True).squeeze().rename('Spot BTC ETF AUM (USD)')
        else:    
            return output_df  

    def get_farside_table(self) -> pd.DataFrame:
        html = get_html_save("https://farside.co.uk/?p=997", save=False)
        soup = BeautifulSoup(html, features="html.parser"); dumpstr = ""
    
        tag = soup.table 
        #export_html(str(tag))
        json_convert = html_to_json(str(tag))
        json_format = json.loads(json_convert)
        #json_file_io(save_load = 'save', json_obj = json_convert, filename = wd+fdel+"farside_etf_flows.json")
        
        i = 0
        for date in json_format:
            df = pd.json_normalize(date).replace({"-": "0.0"}, regex=True).replace({"\(": "-", "\)": "", ",": ""}, regex=True)
            if i == 0: 
                output = df
            else:
                output = pd.concat([output, df], axis = 0)
            i += 1    
       
        output.columns = output.columns.str.strip().str.upper()
        output.set_index("DATE", drop = True, inplace=True)     
        output = output.iloc[:-4].astype("float")

        # Convert index to datetime
        index = pd.DatetimeIndex(pd.to_datetime(output.index, format='%d %b %Y', errors='coerce').date).dropna()
     
        output.set_index(index, drop = True, inplace = True)
        output = output.loc[~output.index.duplicated(keep='first')]
        output['Total'] = output[[col for col in output.columns if col != 'TOTAL']].sum(axis=1)

        return output    

def get_hybrid_flows_table():
    dataset_block = btc_etf_data().df
    fs_data = btc_etf_data()
    farside = fs_data.get_farside_table()*1000000
  
    orders = dataset_block.sum(axis = 0)
    orders = orders.abs().sort_values(ascending=False)

    dataset_block = dataset_block.reindex(columns = orders.index)
    output = farside.reindex(columns = orders.index)
    hybrid_df = combine_etf_datasets(dataset_block, output)
    hybrid_df = hybrid_df.astype("float")
    hybrid_df = hybrid_df.loc[(hybrid_df!=0).any(axis=1)]
    
    return hybrid_df

#################### Plotting functions ####################
def plotly_bar(data: pd.DataFrame):
    fig = go.Figure()

        # Add a bar trace for each column (except for 'Category' column)
    for col in data.columns:
        fig.add_trace(go.Bar(x=data.index, y=data[col], name=col))

    # Customize layout
    fig.update_layout(
        title='Bar chart',
        xaxis_title='Category',
        yaxis_title='Value',
        barmode='group'  # 'group' for grouped bar chart, 'stack' for stacked bar chart
    )

    fig.show()

def px_bar(data:pd.DataFrame):
    fig = px.bar(data, x=data.index, y=data.columns, title = "BTC ETF Flows")
    # Set the number of x ticks
    fig.update_xaxes(nticks=10, showgrid=True)
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    fig.show()

def mpl_bar(data: pd.DataFrame):
    num_vars = len(data.columns) - 1
    bar_width = 0.15
    index = np.arange(len(data.index))

    fig, ax = plt.subplots()

    for i, col in enumerate(data.columns[1:]):
        ax.bar(index + i * bar_width, data[col], bar_width, label=col)

    ax.set_xlabel('Category')
    ax.set_ylabel('Value')
    ax.set_title('Bar chart')
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(data.index)
    ax.legend()

    return fig  

def calculate_dtick(data: pd.DataFrame, num_ticks: int, round: bool = False):
    data_range = data.values.max() - data.values.min()
    dtick = data_range / num_ticks
    if round:
        # Define the "appropriate" numbers
        appropriate_numbers = generate_appropriate_numbers(abs(data.values).max())
        # Find the closest "appropriate" number to dtick
        dtick = min(appropriate_numbers, key=lambda x:abs(x-dtick))
    return dtick   

def generate_appropriate_numbers(max_value):
    factors = [2, 2.5, 2]
    appropriate_numbers = [0.1]
    while appropriate_numbers[-1] < max_value:
        next_number = appropriate_numbers[-1] * factors[len(appropriate_numbers) % len(factors)]
        appropriate_numbers.append(next_number)
    return appropriate_numbers 

def plotly_bar_fullpage(data: pd.DataFrame, custom_index = None):
    fig = go.Figure()
    if custom_index is not None:
        for col in data.columns:
            fig.add_trace(go.Bar(name=col, x=custom_index, y=data[col])) 
    else:        
        for col in data.columns:
            fig.add_trace(go.Bar(name=col, x=data.index, y=data[col]))  # Increase width of the bars

    # Change the bar mode
    fig.update_layout(barmode='group')  

    dtick = calculate_dtick(data, 15, round = True); print(dtick)
    fig.update_layout(yaxis=dict(showgrid=True, gridwidth=1, gridcolor='Black', tickfont=dict(size=15), dtick = dtick, tick0=0, ticklen=10, 
                               tickwidth=2, showline=True, linewidth=2, linecolor='black', mirror=True)) 
    fig.update_layout(legend=dict(x=1.01, y=1, traceorder="normal", font=dict(family="Times New Roman, Times, Serif", size=14, color="black"), 
                              bgcolor="LightSteelBlue", bordercolor="Black", borderwidth=2),
                  legend_title=dict(text="<b>U.S Spot BTC ETF's<b>", font=dict(size=18, color="black"))) 
    fig.update_layout(title=dict(text="<b>Bitcoin ETF flows<b>", x=0.5, font=dict(size=32, color="black")), 
                      xaxis_title="Date",yaxis_title="<b>USD flow into out/of ETF that day<b>", legend_title="<b>U.S Spot BTC ETF's<b>",
                      font=dict(family="Times New Roman, Times, Serif", size=20, color="black"))

    fig.update_layout(showlegend=True, xaxis_showgrid=True, yaxis_showgrid=True, 
                xaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True, type="category"),
            yaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True))

    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="category", showgrid=True, gridwidth=1, gridcolor='Black'))# Add x-grid
    fig.update_layout(shapes=[dict(type="rect",xref="paper",yref="paper",x0=-0.005,y0=-0.27,x1=1.005,y1=-0.07,line=dict(color="Black",width=2),)])

    return fig 

def plotly_bar_sl(data: pd.DataFrame, custom_index=None, width = None, height = None):
    fig = go.Figure()

    if custom_index is not None:
        for col in data.columns:
            fig.add_trace(go.Bar(name=col, x=custom_index, y=data[col]))
    else:
        for col in data.columns:
            fig.add_trace(go.Bar(name=col, x=data.index, y=data[col]))  # Increase width of the bars

    # Change the bar mode
    fig.update_layout(barmode='group')

    dtick = calculate_dtick(data, 8, round=True)

    fig.update_layout(
        yaxis=dict(showgrid=True, tickfont=dict(size=15), dtick=dtick, tick0=0, ticklen=10,
                   tickwidth=2, showline=True, linewidth=1, linecolor='white'),
        yaxis_title="<b>USD flow into out/of ETF that day<b>",
        font=dict(family="Times New Roman, Times, Serif", color="black"),
        showlegend=True,
        xaxis_showgrid=True,
        yaxis_showgrid=True,
        xaxis=dict(type="category")
    )

    fig.update_xaxes(tickfont=dict(color='white'))
    fig.update_yaxes(tickfont=dict(color='white'))

    if width is not None and height is not None:
        # Specify width and height of the figure
        fig.update_layout(width=width, height=height)

    # Add a range slider below the plot increasing height
    fig.update_layout(
        xaxis=dict(rangeslider=dict(visible=True),
                   showgrid=True,
                   showline=True,
                   linewidth=1,
                   linecolor='white')
    )
    # Put legend at the bottom between date slider and date ticks
    fig.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1.04, xanchor='left', x=0.01))

    return fig

def plotly_pie(data: pd.Series, title: str = "Pie chart"):
    fig = px.pie(data, values=data.values, names=data.index, title=title)
    return fig

if __name__ == "__main__":
    hybrid_df = get_hybrid_flows_table()
    hybrid_df.index.rename('Date', inplace=True)

    first_four = hybrid_df.iloc[:, :4]
    sum_others = hybrid_df.iloc[:, 4:].sum(axis=1)
    short_df = first_four.assign(SumOthers=sum_others).rename(columns={'SumOthers': 'Others'})
    net_flow = short_df.sum(axis=1).rename('Net flow total (USD)')
    short_df2 = pd.concat([short_df, net_flow], axis=1)
    custom_index = short_df.index.strftime('%Y-%m-%d')

    fig = charts.altair_line(hybrid_df, right_columns = ['GBTC'])
    fig.show()
    #hydrid_df.to_excel(wd+fdel+"Hybrid_flowz_table.xlsx")
    # hydrid_df.plot(kind='bar', stacked=False, figsize=(10,7))
    # plt.title('Bar Chart of Data')
    # plt.ylabel('Value')
    # plt.xlabel('Date')
    # plt.show()

    # df2.to_csv(wd+fdel+"FarsideLastWeek.csv")
    # dataset_block.to_csv(wd+fdel+"TheBlockData.csv")

