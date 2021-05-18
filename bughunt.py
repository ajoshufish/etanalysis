import streamlit as st
from datetime import time
minTime = time(6,00)
maxTime = time(23,00)
defaultMin = time(10,00)
defaultMax = time(20,00)
time1, time2 = st.sidebar.slider('Time of day?', min_value=minTime, max_value=maxTime, value=(defaultMin, defaultMax), format="LT")
