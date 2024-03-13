import altair as alt
import pandas as pd

def altair_line(df: pd.DataFrame, right_columns: list):
    #Melting the DataFrame to long format for easier plotting with Altair
    df.index.rename('Date', inplace=True)
   
    # Splitting the DataFrame into two based on the category for dual-axis plotting
    df_left = df.copy().drop(right_columns)
    df_right = df[df['category'].isin(right_columns)]
    left_long = df_left.reset_index().melt('Date', var_name='ETF', value_name='ETF Flow (USD)')
    right_long = df_right.reset_index().melt('Date', var_name='ETF', value_name='ETF Flow (USD)')

    # Creating the left axis chart
    left_chart = alt.Chart(df_left).mark_line().encode(
        x='x',
        y=alt.Y('y', axis=alt.Axis(title='Left axis')),
        color='category')

    # Creating the right axis chart
    right_chart = alt.Chart(df_right).mark_line().encode(
        x='x',
        y=alt.Y('y', axis=alt.Axis(title='Right axis'), scale=alt.Scale(domain=[df_right['y'].min(), df_right['y'].max()])),
        color='category')

    # Combining the charts
    combined_chart = alt.layer(left_chart, right_chart).resolve_scale(
        y='independent')
    return combined_chart
