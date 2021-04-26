import streamlit as st
import pandas as pd
pd.options.plotting.backend = "plotly"
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




#get our data loaded in and into a pandas dataframe
data = load_data()
headers = data.pop(0)
df = pd.DataFrame(data, columns=headers)


#snag Columbia data and display
coloData = pd.DataFrame([df['DateTime'],df['Columbia Occupancy'], df['Columbia Capacity']]).T
coloFig = coloData.plot(title="Columbia Occupancy Over Time", x="DateTime", y=["Columbia Occupancy",'Columbia Capacity'], template="simple_white", labels={"DateTime": "Date",'variable':'Values'})
coloFig.update_layout(hovermode='y unified')
st.plotly_chart(coloFig)

#st.line_chart(plot_t)
if st.checkbox('Show Data'):
    st.write(coloData)

