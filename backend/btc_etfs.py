import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import re
import json
import os
from . import charts

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
                "exGBTC_etf_aum_hist": block_base_url+"spot-bitcoin-etf-aum-ex-gbtc-daily",
                "btc_holdings": block_base_url+"spot-bitcoin-etf-onchain-holdings"},
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
    last_block_day = dataset_block.index[-1]
    fs_data = btc_etf_data()
    farside = fs_data.get_farside_table()*1000000
  
    orders = dataset_block.sum(axis = 0)
    orders = orders.abs().sort_values(ascending=False)

    dataset_block = dataset_block.reindex(columns = orders.index)
    output = farside.reindex(columns = orders.index)
    hybrid_df = combine_etf_datasets(dataset_block, output)
    hybrid_df = hybrid_df.astype("float")
    hybrid_df = hybrid_df.loc[(hybrid_df!=0).any(axis=1)]
    
    return hybrid_df, last_block_day

if __name__ == "__main__":
    hybrid_df, cunt = get_hybrid_flows_table()
    hybrid_df.index.rename('Date', inplace=True)

    #hybrid_df.to_excel(wd+fdel+"Hybrid_flowz_table.xlsx")
    print(hybrid_df)
    quit()
    hybrid_df = pd.read_excel(wd+fdel+"Hybrid_flowz_table.xlsx", index_col = 0)
    first_four = hybrid_df.iloc[:, :4]
    sum_others = hybrid_df.iloc[:, 4:].sum(axis=1)
    short_df = first_four.assign(SumOthers=sum_others).rename(columns={'SumOthers': 'Others'})
    net_flow = short_df.sum(axis=1).rename('Net flow total (USD)')
    short_df2 = pd.concat([short_df, net_flow], axis=1)
    custom_index = short_df.index.strftime('%Y-%m-%d')

    fig = charts.altair_line(hybrid_df, right_columns = ['GBTC'])
 
    #hydrid_df.to_excel(wd+fdel+"Hybrid_flowz_table.xlsx")
    # hydrid_df.plot(kind='bar', stacked=False, figsize=(10,7))
    # plt.title('Bar Chart of Data')
    # plt.ylabel('Value')
    # plt.xlabel('Date')
    # plt.show()

    # df2.to_csv(wd+fdel+"FarsideLastWeek.csv")
    # dataset_block.to_csv(wd+fdel+"TheBlockData.csv")

