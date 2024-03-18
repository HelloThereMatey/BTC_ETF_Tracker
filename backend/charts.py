import altair as alt
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np
import os

fdel = os.path.sep
wd = os.path.dirname(__file__)  ## This gets the working directory which is the folder where you have placed this .py file. 
parent = os.path.dirname(wd)

def altair_line(df: pd.DataFrame, right_columns: list, axis_title: str = "USD"):
    #Melting the DataFrame to long format for easier plotting with Altair
    df.index.rename('Date', inplace=True)
   
    # Splitting the DataFrame into two based on the category for dual-axis plotting
    datf = df.copy()
    df_right = datf[right_columns]
    df_left = datf.drop(right_columns, axis = 1)
    left_long = df_left.reset_index().melt('Date', var_name='ETF', value_name='ETF Flow (USD)')
    right_long = df_right.reset_index().melt('Date', var_name='ETF', value_name='ETF Flow (USD)')

    # Creating the left axis chart
    left_chart = alt.Chart(left_long).mark_line().encode(
        x='Date',
        y=alt.Y('ETF Flow (USD)', axis=alt.Axis(title= axis_title)),
        color='ETF'
    )

    # Creating the right axis chart
    right_chart = alt.Chart(right_long).mark_line().encode(
        x='Date',
        y=alt.Y('ETF Flow (USD)', axis=alt.Axis(title= axis_title)), #scale=alt.Scale(domain=[df_right['ETF Flow (USD)'].min(), df_right['ETF Flow (USD)'].max()])),
        color='ETF'
    )

    # Combining the charts
    combined_chart = alt.layer(left_chart, right_chart).resolve_scale(y='independent')
    # combined_chart = combined_chart.configure_legend(orient = 'none',
    # legendX=0.02, legendY=1.1, direction='horizontal',  # Attempt to set legend items horizontally
    # )
    return combined_chart

def plotly_bar_sl(data: pd.DataFrame, custom_index=None, width = None, height = None, ytitle: str = "USD"):
    fig = go.Figure()

    if custom_index is not None:
        for col in data.columns:
            fig.add_trace(go.Bar(name=col, x=custom_index, y=data[col]))
    else:
        for col in data.columns:
            fig.add_trace(go.Bar(name=col, x=data.index, y=data[col]))  # Increase width of the bars

    # Change the bar mode
    fig.update_layout(barmode='group')
    # Cast the spell to set the dark theme
    fig.update_layout(template="plotly_dark")

    datarange = data.values.max() - data.values.min()
    numticks = 8
    
    fig.update_layout(
        yaxis=dict(showgrid=True, tickfont=dict(size=15), dtick=datarange/numticks, tick0=0, ticklen=10,
                   tickwidth=2, showline=True, linewidth=1, linecolor='white'),
        yaxis_title="<b>"+ytitle+"<b>",
        #font=dict(family="Times New Roman, Times, Serif", color="black"),
        showlegend=True,
        xaxis_showgrid=True,
        yaxis_showgrid=True,
        xaxis=dict(type="category")
    )

    # Update the X-axis to display dates in 'YYYY-MM-DD' format
    fig.update_xaxes(tickformat="%Y-%m-%d")

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

def plotly_pie(data: pd.Series, title: str = "Pie chart"):
    fig = px.pie(data, values=data.values, names=data.index, title=title)
    return fig


if __name__ == "__main__":
    
    data = pd.read_excel(wd+fdel+"Hybrid_flowz_table.xlsx", index_col=0)
    index = data.index.strftime('%Y-%m-%d')
    print(type(data.index))
    fig = plotly_bar_sl(data, custom_index=index, width = 1000, height = 700)
    fig.show()