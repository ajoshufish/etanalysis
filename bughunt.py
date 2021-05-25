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
