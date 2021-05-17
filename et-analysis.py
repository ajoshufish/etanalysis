import streamlit as st
import pandas as pd
pd.options.plotting.backend = "plotly"
import gspread
import os
import plotly.graph_objects as go 
st.set_page_config(layout='wide')
from datetime import datetime
from datetime import time

st.title('Earth Treks Occupancy Analysis')

#setup credentials
credentials = {
  "type": st.secrets["type"],
  "project_id": st.secrets["project_id"],
  "private_key_id": st.secrets["private_key_id"],
  "private_key": st.secrets["private_key"],
  "client_email": st.secrets["client_email"],
  "client_id": st.secrets["client_id"],
  "auth_uri": st.secrets["auth_uri"],
  "token_uri": st.secrets["token_uri"],
  "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
  "client_x509_cert_url": st.secrets["client_x509_cert_url"]
  }
sheetKey = st.secrets["worksheet_key"]
dbSheet = st.secrets["sheet"]

#Load up all our data
@st.cache(allow_output_mutation=True)
def load_dataset():
   gc = gspread.service_account_from_dict(credentials)
   ws = gc.open_by_key(sheetKey).worksheet(dbSheet)
   return ws.get_all_records()


#get our data loaded in and into a pandas dataframe
data = load_dataset()
headers = data.pop(0)
df = pd.DataFrame(data, columns=headers)

#choose location and setup localized data
gym = st.sidebar.selectbox('Which gym should we look at?', ['Columbia', 'Hampden', 'Timonium', 'Crystal City', 'Rockville'])
gymOcc = gym + ' Occupancy'
gymCap = gym + ' Capacity'
gymData = pd.DataFrame([df['DateTime'],df[gymOcc], df[gymCap], df['Day']]).T
gymData['DateTime'] = pd.to_datetime(gymData['DateTime'])
gymData['Time'] = gymData['DateTime'].dt.strftime('%l:%M %p')
gymData['CTime'] = gymData['DateTime'].dt.time
gymData['ShDay'] = gymData['DateTime'].dt.strftime('%a')
gymData['Date'] = gymData['DateTime'].dt.strftime('%b %e')


#Get options
st.sidebar.text('Filter the data?')
filtDays = st.sidebar.multiselect('Day of the week?', ('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'))
filtTime1, filtTime2 = st.sidebar.slider('Time of day?', min_value=time(6,00), max_value=time(23,00), value=(time(10,00), time(20,00)))

#filter our data
opts = 'Day =='
filt = gymData
if(len(filtDays) > 0):
    for index, items in enumerate(filtDays):
        opts = opts + '"'+filtDays[index]+'"'
        if (len(filtDays) - index -1> 0):
            opts = opts + " or Day == "

    filt = filt.query(opts)
filt = filt[filt.CTime >= filtTime1]
filt = filt[filt.CTime <= filtTime2]

#plot it
st.text("What's been going on at "+ gym+ ' ?')
colorhelp = 'rgba(0,0,0,0)'
fig = go.Figure()
fig.add_trace(go.Scatter(name='', y=filt[gymOcc], x=filt['DateTime'], mode='markers+lines', hovertemplate='Occupancy: %{y} at %{text}', text=filt['Time'] + ' on '+ filt['ShDay'] +', ' + filt['Date']))
fig.add_trace(go.Scatter(name='', y=filt[gymCap], x=filt['DateTime'], hovertemplate='Capacity: %{y} (%{text})', text=filt['Date']))
fig.update_layout(xaxis_title='Date', yaxis_title='Occupancy', yaxis=dict(showspikes=True, spikemode = 'marker+toaxis', spikesnap = 'cursor'), xaxis=dict(type = "category", showspikes=True, spikemode = 'marker+toaxis', spikesnap = 'cursor'), margin_l=10, margin_r=10, margin_t=10, margin_b=10, hovermode='closest', showlegend=False)
fig.update_xaxes(rangeslider_visible=True, tickvals=['one', 'two'], ticktext=[filt['DateTime'].dt.strftime('%m%d')])
st.plotly_chart(fig , use_container_width=True)

#debug/raw data
if st.checkbox('Show Data'):
    st.write(filt)

