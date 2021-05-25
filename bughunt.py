import streamlit as st
from datetime import time
from datetime import datetime as dt


minTime = time(6,00)
maxTime = time(23,00)
defaultMin = time(10,00)
defaultMax = time(20,00)

# minTime =  6
# maxTime = 23
# defaultMin = 10
# defaultMax = 20
st.slider('Start of time range?', min_value=minTime, max_value=maxTime, value=defaultMin)
st.slider('End of time range?', min_value=minTime, max_value=maxTime, value=defaultMax)

times=['6:00 AM', '7:00 AM', '8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM', '1:00 PM', '1:00 PM', '3:00 PM', '4:00 PM', '5:00 PM', '6:00 PM', '7:00 PM', '8:00 PM', '9:00 PM', '10:00 PM', '11:00 PM']
time1, time2 = st.select_slider('Choose range', options=times, value=('7:00 AM', '1:00 PM'))
st.write(time1)
st.write(time2)
st.write(dt.strptime(time1, '%I:%M %p').time())
st.write(dt.strptime(time2, '%I:%M %p').time())

