#Using Python 3.7
#with packages below
import plotly.express as px
import pandas as pd
from datetime import datetime, date, timedelta
from urllib.request import urlopen
import csv
from csv import reader
import json

def makeDateTime(datein): #date is in mm-dd-yyyy format
    hyph1 = str(datein).find("-")
    month = str(datein)[0:hyph1]
    hyph2 = str(datein).find("-",hyph1+1)
    day = str(datein)[hyph1+1:hyph2]
    year = str(datein)[hyph2+1:]
    return date(int(year),int(month),int(day))



with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

import pandas as pd
#df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
#                   dtype={"fips": str})
df = pd.read_csv("all_days.csv",
                  dtype={"FIPS": str})
#get the list of fips to process
list_of_fips = []
#and the most current date
two_weeks_ago = date.today() -timedelta(14)
latest_date = two_weeks_ago
with open("all_days.csv", 'r') as csvfile:
    list_of_rows = reader(csvfile)
    list_of_records = list(list_of_rows)
    for countyDate in list_of_records[1:]:
        if countyDate[0] not in list_of_fips:
            list_of_fips.append(countyDate[0])
        #create a datetime.date
        newDate = makeDateTime(countyDate[2]) # mm-dd-yyyy
        if newDate  >  latest_date:
            latest_date = newDate

Period = 7  #set averaging period in days
interval_days = []
for i in range(0,5):
    endpoint = latest_date - timedelta(i*Period)
    year = endpoint.year
    month = endpoint.month
    day = endpoint.day
    if(len(str(day)) == 1):
        day = "0"+str(day)
    endpoint_day_string = str(month) + '-' + str(day) + '-' + str(year)
    interval_days.append(endpoint_day_string)
dataframe_list = []
for fip in list_of_fips:
    df_fip = df[df['FIPS']==fip]  # get all measurements in that FIP locality
    # now grab all the period endpoint
    confirmed = []
    deaths = []

    for index,end_point in enumerate(interval_days):
        #we need to put this is a try statement
        try:
            element = int(df_fip[df_fip['file_date'] == end_point].loc[:, 'Confirmed'].values[0]) #rows is an array

            confirmed.append(element)
            element = int(df_fip[df_fip['file_date'] == end_point].loc[:, 'Deaths'].values[0])  # rows is an array

            deaths.append(element)
            index_fip = index #some fips don't have complete date histories
        except:

           # print(fip + " has an incomplete date history")
           # print(len(confirmed)-1)


            break
    index_fip = len(confirmed)-1
    if index_fip < 0:
        index_fip = 0
    #Now create the vector of info for this FIP location
    confirmed_diff = []
    for index in range(0,index_fip):
        confirmed_diff.append( float(confirmed[index]) - float(confirmed[index+1])) #change frokm int to a float
    try:
        if float(confirmed_diff[1]) > 0.0:
            change_percent_confirm = -100.0*float(confirmed_diff[1]-confirmed_diff[0])/float(confirmed_diff[1])
        else:
            change_percent_confirm = 0
    except:
        change_percent_confirm = 0
    deaths_diff = []
    for index in range(0,index_fip):
        deaths_diff.append( int(deaths[index]) - int(deaths[index+1]))
    try:
        if float(deaths_diff[1]) > 0.0:
            change_percent_deaths = -100.*float(deaths_diff[1]-deaths_diff[0])/float(deaths_diff[1])
        else:
            change_percent_deaths = 0
    except:
        change_percent_deaths = 0
    # FIPS | location | date | Confirmed | Deaths | Change Confirmed % | Change Deaths % ! New Confirmed Current | New Confirmed Current -1
    # New Confirmed Current -2 | New Confirmed Current -3 |New Confirmed Current - 4 | New Deaths Current | New Deaths Current -1
    #     # New Deaths Current -2 | New Deaths Current -3 |New Deaths Current - 4

    if len(fip) == 4:  #must have removed the leading zero
        fips_v = "0"+str(fip)
    else:
        fips_v = str(fip)

    location_v = str(df_fip.loc[:, 'location'].values[0])

    date_v = interval_days[0]
    try:
        confirmed_v = int(df_fip[df_fip['file_date'] == interval_days[0]].loc[:, 'Confirmed'].values[0])
        deaths_v = int(df_fip[df_fip['file_date'] == interval_days[0]].loc[:, 'Deaths'].values[0])
    except:
        confirmed_v = int(df_fip.loc[:, 'Confirmed'].values[0])
        deaths_v = int(df_fip.loc[:, 'Deaths'].values[0])

    location_date_record = [fips_v,location_v,date_v,confirmed_v,deaths_v,change_percent_confirm,change_percent_deaths]
    for i in range(0,index_fip):
        location_date_record.append(confirmed_diff[i])
    #take care of the short dated fip
    if int(len(interval_days)-1-index_fip) != 0:
        for i in range(0,int(len(interval_days)-1-index_fip)):
                location_date_record.append(0) #I changed this from blank to zero for plotting reasons

    for i in range(0,index_fip):
        location_date_record.append(deaths_diff[i])
    if int(len(interval_days) - 1 - index_fip) != 0:
        for i in range(0, int(len(interval_days)-1 - index_fip)):
            location_date_record.append(0) #I changed this from blank to zero for plotting reasons
    #ok now the vector of all the possible items we might want to display on the hover or on the graph are accounted for
    dataframe_list.append(location_date_record)

    if len(location_date_record) != 15:
        print("Len of record = ", len(location_date_record))
        break
# now create the header
header = ["FIPS","location","date", "Confirmed","Deaths","Change_Confirmed_%", "Change_Deaths_%"]
header.append("New_Confirmed_Current")
for i in range(1,len(interval_days)-1):
    header.append("New_Confirmed_Current-" + str(i))
header.append("New_Deaths_Current")
for i in range(1,len(interval_days)-1):
    header.append("New_Deaths_Current-" + str(i))

dfchange = pd.DataFrame(dataframe_list,columns = header) # this is the complete dataframe with 15 columns
# FIPS | location | date | Confirmed | Deaths | Change_Confirmed_% | Change_Deaths_% ! New_Confirmed_Current | New_Confirmed_Current-1
# New_Confirmed_Current-2 | New_Confirmed_Current-3 |New_Confirmed_Current-4 | New_Deaths_Current | New Deaths Current -1
#     # New Deaths Current -2 | New Deaths Current -3 |New Deaths Current - 4
#choose the columns you want for the plot

#OK now lets plot it:
import plotly.express as px
import pandas as pd
from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)
import plotly.express as px

fig = px.choropleth(dfchange, geojson=counties, locations='FIPS', color="New_Deaths_Current", #geojson=counties

                           color_continuous_scale="Rainbow",#Viridis",
                           range_color=(0, 50),
                           scope="usa",
                          # labels = False,
                           labels={"FIPS":"Location Index","New_Deaths_Current":"Deaths Last Week"},

                           #locationmode="USA-states",
                           hover_name = "location",


                          hover_data =["Change_Deaths_%","New_Deaths_Current-1","New_Deaths_Current-2","New_Deaths_Current-3"]

                          )
fig.update_layout(margin={"r":0,"t":25,"l":0,"b":0},

                  title_text = "Weekly Deaths "+ date_v +"; Hover shows % Change and weekly deaths back in time",

                  geo = dict(
                             showcoastlines=False,
                             showcountries = True

                            )


                  )

fig.show()
