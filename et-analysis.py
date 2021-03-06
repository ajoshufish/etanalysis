import streamlit as st
import pandas as pd
import gspread
import plotly.graph_objects as go 
st.set_page_config(layout='wide')
from datetime import datetime
from datetime import timedelta as td
from datetime import time
import pytz as tz

st.title('Earth Treks Occupancy Analysis')

if st.checkbox('Show Description'):
    st.info('The COVID-19 pandemic dramatically changed the way climbers interface with their local climbing gyms. \nReservation systems, masks, and capacity limits have all been standard. In order to make informed decisions \nabout when is a good time to go to the gym (that is to say, when it\'s not totally full of other people),\nI put together this tool. We pull their data here and there throughout the main hours the local gyms are open\nand feed it into this tool by bouncing it off a Google Sheet.')

# setup credentials
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

# Load up all our data
@st.cache(ttl=1100, allow_output_mutation=True)
def load_dataset():
   gc = gspread.service_account_from_dict(credentials)
   ws = gc.open_by_key(sheetKey).worksheet(dbSheet)
   return ws.get_all_records()

# get our data loaded in and into a pandas dataframe
data = load_dataset()
headers = data.pop(0)


df = pd.DataFrame(data, columns=headers, copy=True)

# setup starting location data
gym = st.sidebar.selectbox('Which gym should we look at?', ['Columbia', 'Hampden', 'Timonium', 'Crystal City', 'Rockville'])
gymOcc = gym + ' Occupancy'
gymCap = gym + ' Capacity'
gymData = pd.DataFrame([df['DateTime'],df[gymOcc], df[gymCap], df['Day']]).T
gymData['DateTime'] = pd.to_datetime(gymData['DateTime'])
gymData['Time'] = gymData['DateTime'].dt.strftime('%l:%M %p')
gymData['CTime'] = gymData['DateTime'].dt.time
gymData['ShDay'] = gymData['DateTime'].dt.strftime('%a')
gymData['Date'] = gymData['DateTime'].dt.strftime('%b %e')

# Get options   
with st.sidebar:
    with st.form(key='opts_form'):
        st.text('Select options for filtering:')
        filtDays = st.multiselect('Day of the week? (default: all)', ('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'))

        # deployed streamlit's datetime range slider is bugged, so we hack together a working solution by passing it through a string
        # first we generate a bunch of datetimes using pandas, then turn them into strings, format them, use them as string options, 
        # then convert them back to a time datatype that we can use in future datetime comparisons. The gyms don't open before 6a or 
        # stay open after 11, so those are out limiters on the range, set in this first line.
        bundletimes = pd.date_range('6:00', '23:00', freq='10 min')
        bundletimes = [datetime.strftime(a, '%l:%M %p').split(' ', 1)[1] if datetime.strftime(a, '%l:%M %p')[0]==' ' else datetime.strftime(a, '%l:%M %p') for a in bundletimes]
        time1, time2 = st.select_slider('Time of day?', options=bundletimes, value=('7:00 AM', '1:00 PM'))
        time1 = datetime.strptime(time1, '%I:%M %p').time()
        time2 = datetime.strptime(time2, '%I:%M %p').time()
        
        submit_button = st.form_submit_button(label='Submit')
    

# apply our options to filter our data
opts = 'Day =='
filt = gymData.copy()
if(len(filtDays) > 0):
    for index, items in enumerate(filtDays):
        opts = opts + '"'+filtDays[index]+'"'
        if (len(filtDays) - index -1> 0):
            opts = opts + " or Day == "
    filt = filt.query(opts)
filt = filt[filt.CTime >= time1]
filt = filt[filt.CTime <= time2]

# ugly way to handle this, building a df from scratch with each gym's weekly hours. 
# this could be improved by scraping from the website perhaps
gymTimeHead = ['Gym', 'WeekOpen', 'WeekClose', 'SatOpen', 'SatClose', 'SunOpen', 'SunClose']
timTime = ['Timonium', time(16,00), time(22,00), time(9,00), time(16,00), time(9,00), time(16,00)]
coloTime = ['Columbia', time(6,00), time(23,00), time(8,00), time(20,00), time(8,00), time(18,00)]
rocTime = ['Rockville', time(6,00), time(23,00), time(8,00), time(20,00), time(8,00), time(18,00)]
hamTime = ['Hampden', time(6,00), time(22,00), time(8,00), time(20,00), time(8,00), time(18,00)]
cryTime = ['Crystal City', time(6,00), time(23,00), time(8,00), time(20,00), time(8,00), time(18,00)]
gymTime = pd.DataFrame(list(zip(timTime, coloTime, rocTime, hamTime, cryTime))).T
gymTime.columns = gymTimeHead

# programmatically find days we didn't collect data so we can filter them out on a plotting level
dt_all = pd.date_range(start=filt['DateTime'].iloc[0], end=filt['DateTime'].iloc[-1], freq='H')
dt_obs = [d.strftime('%Y-%m-%d') for d in filt['DateTime']]
dt_breaks = [d for d in dt_all.strftime('%Y-%m-%d').tolist() if not d in dt_obs]
dt_breaks = list(dict.fromkeys(dt_breaks))

# plot it
st.text("What's been going on at "+ gym+ ' ?')
colorhelp = 'rgba(0,0,0,0)'
fig = go.Figure()
fig.add_trace(go.Scatter(name='', y=filt[gymOcc], x=filt['DateTime'], mode='markers+lines', 
    hovertemplate='Occupancy: %{y} at %{text}', text=filt['Time'] + ' on '+ filt['ShDay'] +', ' + filt['Date']))

fig.add_trace(go.Scatter(name='', y=filt[gymCap], x=filt['DateTime'], hovertemplate='Capacity: %{y} (%{text})', 
    text=filt['Date']))

fig.update_layout(xaxis_title='Date', yaxis_title='Occupancy',
    yaxis=dict(showspikes=True, spikemode = 'marker+toaxis', spikesnap = 'cursor'), 
    xaxis=dict(showspikes=True, spikemode = 'marker+toaxis', spikesnap = 'cursor'), 
    margin_l=10, margin_r=10, margin_t=10, margin_b=10, hovermode='closest', showlegend=False)

fig.update_xaxes(rangeslider_visible=True, rangebreaks=[dict(values=dt_breaks)])
st.plotly_chart(fig , use_container_width=True)

# show raw data
#if st.checkbox('Show Data'):
#    st.write(filt)

# here we pull out some data on the gym in question, such as hours of operation
# and what things typically look like at this time.
st.title('Selected Gym Info: ' +gym)
col1, col2 = st.beta_columns(2)

with col1:
    st.write('Weekday Open: ' + gymTime.loc[gymTime.Gym == gym]['WeekOpen'].values[0].strftime('%l:%M %p'))
    st.write('Weekday Close: ' + gymTime.loc[gymTime.Gym == gym]['WeekClose'].values[0].strftime('%l:%M %p'))
    st.write('Saturday Open: ' + gymTime.loc[gymTime.Gym == gym]['SatOpen'].values[0].strftime('%l:%M %p'))
    st.write('Saturday Close: ' + gymTime.loc[gymTime.Gym == gym]['SatClose'].values[0].strftime('%l:%M %p'))
    st.write('Sunday Open: ' + gymTime.loc[gymTime.Gym == gym]['SunOpen'].values[0].strftime('%l:%M %p'))
    st.write('Sunday Close: ' + gymTime.loc[gymTime.Gym == gym]['SunClose'].values[0].strftime('%l:%M %p'))
with col2:
    st.write('Capacity: ' + str(filt[gymCap][filt.index[-1]]))
    st.write('Current Occupancy: '+ str(filt[gymOcc][filt.index[-1]]))
    
    # make sure we localize all these to ET timezone
    st.write('The time now is about ' + datetime.now(tz.timezone('America/New_York')).time().strftime('%l:%M %p') + ' on a ' +datetime.now(tz.timezone('America/New_York')).strftime('%A'))
    
    # we look 40 minutes in either direction from now and then average the occupancy numbers in that time on this day
    lowEnd = (datetime.now(tz.timezone('America/New_York')) - td(minutes=40)).time()
    highEnd = (datetime.now(tz.timezone('America/New_York')) + td(minutes=40)).time()
    timeBand = gymData[(gymData['CTime'] >= lowEnd) & (gymData['ShDay'] == datetime.now(tz.timezone('America/New_York')).strftime('%a')) & (gymData['CTime'] <= highEnd)]
    st.write('Typically, near this time/day the gym has about ' + str(timeBand[gym + ' Occupancy'].mean().astype(int)) + ' people')
