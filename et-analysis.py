import streamlit as st
import pandas as pd
pd.options.plotting.backend = "plotly"
import gspread
import os
import plotly.graph_objects as go 
import plotly_express as px
st.set_page_config(layout='wide')
from datetime import datetime
from datetime import time

st.title('Earth Treks Occupancy Analysis')

#cache our data pulling
@st.cache(allow_output_mutation=True)
def load_data():
    filefold = os.path.dirname(os.path.abspath(__file__))
    authpath = os.path.join(filefold, 'etdataaccess.json')
    gc = gspread.service_account(authpath)
    ws = gc.open_by_key("1pAzzV_ywejUJKWkkrPSdHfssMp3qcCEbmyK6XiZfxTQ").worksheet('Data')
    return ws.get_all_records()




#get our data loaded in and into a pandas dataframe
data = load_data()
headers = data.pop(0)
df = pd.DataFrame(data, columns=headers)


#snag Columbia data and parse
coloData = pd.DataFrame([df['DateTime'],df['Columbia Occupancy'], df['Columbia Capacity'], df['Day']]).T
coloData['DateTime'] = pd.to_datetime(coloData['DateTime'])
coloData['Time'] = coloData['DateTime'].dt.strftime('%l:%M %p')
coloData['CTime'] = coloData['DateTime'].dt.time
coloData['ShDay'] = coloData['DateTime'].dt.strftime('%a')
coloData['Date'] = coloData['DateTime'].dt.strftime('%b %e')


#Get options
st.sidebar.text('Filter the data?')
filtDays = st.sidebar.multiselect('Day of the week?', ('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'))
filtTime1, filtTime2 = st.sidebar.slider('Time of day?', min_value=time(6,0), max_value=time(22,00), value=(time(10,00), time(20,00)))

#filter our data
opts = 'Day =='
filt = coloData

if(len(filtDays) > 0):
    for index, items in enumerate(filtDays):
        opts = opts + '"'+filtDays[index]+'"'
        if (len(filtDays) - index -1> 0):
            opts = opts + " or Day == "

    filt = filt.query(opts)

filt = filt[filt.CTime >= filtTime1]
filt = filt[filt.CTime <= filtTime2]

#plot it
colorhelp = 'rgba(0,0,0,0)'
fig = go.Figure()
fig.add_trace(go.Scatter(name='', y=filt['Columbia Occupancy'], x=filt['DateTime'], mode='markers+lines', hovertemplate='Occupancy: %{y} at %{text}', text=filt['Time'] + ' on '+ filt['ShDay'] +', ' + filt['Date']))
fig.add_trace(go.Scatter(name='', y=filt['Columbia Capacity'], x=filt['DateTime'], hovertemplate='Capacity: %{y} (%{text})', text=filt['Date']))
fig.update_layout(xaxis_title='Date', yaxis_title='Occupancy', yaxis=dict(showspikes=True, spikemode = 'marker+toaxis', spikesnap = 'cursor'), xaxis=dict(type = "category", showspikes=True, spikemode = 'marker+toaxis', spikesnap = 'cursor'), margin_l=10, margin_r=10, margin_t=10, margin_b=10, hovermode='closest', showlegend=False)

fig.update_xaxes(rangeslider_visible=True, tickvals=['one', 'two'], ticktext=[filt['DateTime'].dt.strftime('%m%d')])
st.plotly_chart(fig , use_container_width=True)

st.write(filt['Date'].array)

#st.line_chart(plot_t)
if st.checkbox('Show Data'):
    st.write(filt)

