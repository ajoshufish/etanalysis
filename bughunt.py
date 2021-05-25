import streamlit as st
from datetime import time
from datetime import datetime as dt
import pytz

eastern = pytz.timezone("US/Eastern")

base = dt.strptime('6:00', '%H:%M')


est = eastern.localize(base)


conv1 = dt.time(est)
st.write(conv1)

minTime = time(6,00)
maxTime = time(23,00)
defaultMin = time(10,00)
defaultMax = time(20,00)
st.slider('Time of day?', min_value=conv1, max_value=maxTime, value=(defaultMin, defaultMax), format="LT")
