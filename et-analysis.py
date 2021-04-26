import streamlit as st
import pandas as pd
import gspread
import os

st.title('Earth Treks Occupancy Analysis')

#cache our data pulling
@st.cache(allow_output_mutation=True)
def load_data():
    filefold = os.path.dirname(os.path.abspath(__file__))
    authpath = os.path.join(filefold, 'etdataaccess.json')
    gc = gspread.service_account(authpath)
    ws = gc.open_by_key("1pAzzV_ywejUJKWkkrPSdHfssMp3qcCEbmyK6XiZfxTQ").worksheet('Data')
    return ws.get_all_records()


st.text('Loading data...')
data = load_data()
headers = data.pop(0)
df = pd.DataFrame(data, columns=headers)
st.text('Loading data...done!')

col1 = df['Time']
col2 = df['Columbia Occupancy']
combo = [col1,col2]
plots = pd.DataFrame(combo)
plot_t = plots.T

st.line_chart(plot_t)
st.write(plot_t)
