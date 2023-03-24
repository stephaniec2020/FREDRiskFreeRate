import os
import arrow
import streamlit as st
import numpy as np
import altair as alt
import pandas as pd
from fredapi import Fred
from datetime import datetime, timedelta


# title of the app
st.title('Fred Risk Free Rate Data and Curve')

# description of the FRED app
st.write('This is a simple streamlit app that uses FRED data to returns risk-free yield and curve:')
st.markdown("- yield  - this returns a table of the most recent yield rates")
st.markdown("- curve  - shows the yield curve on the most recent rates")

# treasury list
yield_ids = ['DGS1MO','DGS3MO','DGS6MO','DGS1','DGS2','DGS3','DGS5', 'DGS7','DGS10', 'DGS20', 'DGS30' ]

# define time periods
time_periods = ['1 Month', '3 Month', '6 Month', '1 Year', '2 Year', '3 Year', '5 Year', '7 Year', '10 Year', '20 Year', '30 Year']


fred = Fred(api_key=st.secrets["FRED_API_KEY"])
end_date = arrow.now()
start_date = end_date.shift(days=-5)
    
data = pd.DataFrame([
    dict(
    id=x['id'],
    Expiry=x['name'],
    Date=x['series'].index.date[0],
    Rate=x['series'][0]) 
        for x in [
        dict(
            name=name,
            id=yld,
            series=fred.get_series(
            yld,
            observation_start=start_date.format('YYYY-MM-DD'), 
            observation_end=end_date.format('YYYY-MM-DD')).dropna().iloc[-1:]) 
        for yld,name in zip(yield_ids,time_periods)
        ]
])

# st.write - whole data in dataframe
# st.write(data)

rates = data['Rate'].tolist()
dic = dict(zip(rates, time_periods))

# st.selectbox - user can select the yield that they would like to know
option = st.selectbox(
     'Which time period of the yield?', rates, format_func=lambda x: dic[x])

st.write(f"The yield of your selected time period is {option}.") #{data['rate']}

# define reference date (today)
ref_date = datetime.now()

# iterate over time periods and convert to datetime
for period in time_periods:
    if 'Month' in period:
        months = int(period.split()[0])
        end_datetime = ref_date + timedelta(days=30*months)
    elif 'Year' in period:
        years = int(period.split()[0])
        end_datetime = ref_date + timedelta(days=365*years)
    else:
        raise ValueError('Invalid time period')

    print(f'{period} : {end_datetime}')

    data.loc[data['Expiry'] == period] = end_datetime


data_simplified = pd.DataFrame({
    'Expiry': time_periods,
    'Date': data['Expiry'],
    'Rate': rates
})

st.write(data_simplified)

chart=alt.Chart(data_simplified).mark_line().encode(
    x=alt.X('Date:T', axis=alt.Axis(labelAngle=-45)),
    y=alt.Y('Rate', scale=alt.Scale(domain=[2, 6]))
).properties(
    width=600,
    height=400
).interactive()

st.write(chart)