#!/usr/local/bin/python3
import requests
from datetime import datetime
import calendar
import pandas as pd
import gspread
import gspread_dataframe as gd
import os

#snag the page we want to parse
page = requests.get('https://portal.rockgympro.com/portal/public/dd60512aa081d8b38fff4ddbbd364a54/occupancy?&iframeid=occupancyCounter&fId=1160')

#for each gym, figure out where in the page code we want to start and end parsing, then extract out the cap and occ
coloStart = page.text.find("'COL' : {")+8
coloEnd = page.text.find(",'BEL' ")
coloText = page.text[coloStart:coloEnd]
coloContent = coloText.split(":")
coloCapacity = coloContent[1].split(",")[0].split(" ")[1]
coloOccupancy = coloContent[2].split(",")[0].split(" ")[1]

timoStart = page.text.find("'TIM' : {")+8
timoEnd = page.text.find(",'ROC' ")
timoText = page.text[timoStart:timoEnd]
timoContent = timoText.split(":")
timoCapacity = timoContent[1].split(",")[0].split(" ")[1]
timoOccupancy = timoContent[2].split(",")[0].split(" ")[1]

hamStart = page.text.find("'HMD' : {")+8
hamEnd = page.text.find(",'SCA' ")
hamText = page.text[hamStart:hamEnd]
hamContent = hamText.split(":")
hamCapacity = hamContent[1].split(",")[0].split(" ")[1]
hamOccupancy = hamContent[2].split(",")[0].split(" ")[1]

cryStart = page.text.find("'CRY' : {")+8
cryEnd = page.text.find(",'COL' ")
cryText = page.text[cryStart:cryEnd]
cryContent = cryText.split(":")
cryCapacity = cryContent[1].split(",")[0].split(" ")[1]
cryOccupancy = cryContent[2].split(",")[0].split(" ")[1]

rocStart = page.text.find("'ROC' : {")+8
rocEnd = page.text.find(",'CRY' ")
rocText = page.text[rocStart:rocEnd]
rocContent = rocText.split(":")
rocCapacity = rocContent[1].split(",")[0].split(" ")[1]
rocOccupancy = rocContent[2].split(",")[0].split(" ")[1]

#let's save some date information so we know when this was scraped
now = datetime.now()
date = now.strftime("%m/%d/%Y")
time = now.strftime("%H:%M")
day = calendar.day_name[now.weekday()]

#build up a row with all the relevant date and gym info
gymInfo = {'DateTime':now, 'Date':date, 'Time':time, 'Day':day, 'Columbia Capacity':coloCapacity, 'Columbia Occupancy':coloOccupancy, 'Timonium Capacity': timoCapacity, 'Timonium Occupancy': timoOccupancy, 'Hampden Capacity': hamCapacity, 'Hampden Occupancy': hamOccupancy, 'Crystal City Capacity': cryCapacity, 'Crystal City Occupancy': cryOccupancy, 'Rockville Capacity': rocCapacity, 'Rockville Occupancy':rocOccupancy}
gymSer = pd.Series(gymInfo)

#what's the data frame setup we want?
df = pd.DataFrame(columns=('DateTime', 'Date', 'Time', 'Day', 'Columbia Capacity', 'Columbia Occupancy', 'Timonium Capacity', 'Timonium Occupancy', 'Hampden Capacity', 'Hampden Occupancy', 'Crystal City Capacity', 'Crystal City Occupancy', 'Rockville Capacity', 'Rockville Occupancy'))

#helper function to find where in the google sheet do we want to put this new row?
def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return len(str_list)+1

#let's connect to the google sheet. what's our auth info, and then what sheet and specific worksheet do we want?
filefold = os.path.dirname(os.path.abspath(__file__))
authpath = os.path.join(filefold, 'etdataaccess.json')
gc = gspread.service_account(authpath)
ws = gc.open_by_key("1pAzzV_ywejUJKWkkrPSdHfssMp3qcCEbmyK6XiZfxTQ").worksheet('Data')

#for that sheet, where do we want our data to be inserted?
next_row = next_available_row(ws)

#add our row to the data frame
df = df.append(gymSer, ignore_index=True)

#add just that one row to the sheet where we decided we wanted it to live
gd.set_with_dataframe(worksheet=ws,dataframe=df,include_index=False,include_column_header=False,row=next_row,resize=False)

#debug info sending this to a local file
#df.to_csv('out.csv', mode='a', header=False, index=False)

