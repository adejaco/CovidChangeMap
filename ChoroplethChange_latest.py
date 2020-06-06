#Using Python 3.7
#with packages below
import plotly.express as px
import pandas as pd
from datetime import datetime, date, timedelta
from urllib.request import urlopen
import csv
from csv import reader
import json
MAXRANGE = 700

google_script = open("google_tracking_new.txt")
google_str = google_script.read()
google_script.close()
import os
def AddGoogleTracking(filename):

    file = open(filename, 'r')
    file_str = file.read()
    file.close()
    ptr = file_str.find("<head>")
    new_file = file_str[:ptr + len("<head>")] + google_str + file_str[ptr + len("<head>"):]
    os.remove(filename)
    html = open(filename, 'w')
    html.write(new_file)
    html.close()

    return


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
# get the population data for each fip county
with open("fip_county_population.csv", 'r') as csvfile:
    list_of_rows = reader(csvfile)
    list_of_fip_pop = list(list_of_rows)
population = {}
for county in list_of_fip_pop[1:]:
    population[county[0]]=int(str(county[3]).replace(",",""))

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
date_str = str(latest_date.month)+"-"+str(latest_date.day)+"-"+str(latest_date.year)
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
        if confirmed_diff[0] < 0:
            confirmed_diff[0] = 0
    except:
        print('')

    try:

        if float(confirmed_diff[1]) > 0.0:
            change_percent_confirm = str ( ' '+str(round(-100.0*float(confirmed_diff[1]-confirmed_diff[0])/float(confirmed_diff[1]),1)))
            change_confirm = -1 * int(confirmed_diff[1] - confirmed_diff[0])
            change_confirm_per_1000 = round(1000.0*float(change_confirm)/float(population[fip]),2)
        else:
            change_percent_confirm = 0
            change_confirm = 0
            change_confirm_per_1000 = 0.0
    except:
        change_percent_confirm = 0
        change_confirm = 0
        change_confirm_per_1000 = 0.0
    deaths_diff = []
    for index in range(0,index_fip):
        deaths_diff.append( int(deaths[index]) - int(deaths[index+1]))
    try:
        if float(deaths_diff[1]) > 0.0:
            change_percent_deaths = str ( ' '+ str(round(-100.*float(deaths_diff[1]-deaths_diff[0])/float(deaths_diff[1]),1)))
            change_deaths = deaths_diff[0]-deaths_diff[1]
        else:
            change_percent_deaths = 0
            change_deaths = 0
    except:
        change_percent_deaths = 0
        change_deaths = 0
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

     #   location_date_record.append(str(' ' + str(confirmed_diff[i])))
        location_date_record.append(confirmed_diff[i])

    #take care of the short dated fip
    if int(len(interval_days)-1-index_fip) != 0:
        for i in range(0,int(len(interval_days)-1-index_fip)):
                location_date_record.append(0)

    for i in range(0,index_fip):
        location_date_record.append(deaths_diff[i])
    if int(len(interval_days) - 1 - index_fip) != 0:
        for i in range(0, int(len(interval_days)-1 - index_fip)):
                location_date_record.append(0)

            #I changed this from blank to zero for plotting reasons
    #ok now the vector of all the possible items we might want to display on the hover or on the graph are accounted for

    # add quantized color for better mapping results
    # didn't get this to work yet
    range_max = 700
    range_min = 0
    divisions = 5  # make sure you get a delta that is an integer
    delta = int(range_max-range_min)/int(divisions)
    try:
        quantized_index =  int(int(confirmed_diff[0])/int(delta)) # no info for this county for the desired date
    except:
        quantized_index = 0

    if quantized_index >= divisions:
        quantized_color = str(">"+str(range_max))
    else:
        quantized_color = str(int(quantized_index*delta))+" to " +str(int((quantized_index+1)*delta))
        if(int(quantized_index*delta) < 0):
            print('this should never happen')

    category_order_list = []
    for index in range(0, divisions):
        category_order_list.append(
            str(int(range_min + index * delta)) + " to " + str(int((range_min + index + 1) * delta)))
    category_order_list.append(str(">" + str(range_max)))


    location_date_record.append(quantized_color)

# add change by population
    try:
        weekly_per_capita = round(1000.*float(confirmed_diff[0])/float(population[fip]),3)  # no info for this county for the desired date
    except:
        weekly_per_capita = 0.0
    location_date_record.append(weekly_per_capita)
    try:
        location_date_record.append(float(population[fip]))
    except:
        location_date_record.append(0.0)

    range_max = 3.0
    range_min = 0
    divisions = 5  # make sure you get a delta that is an integer
    delta = float(range_max - range_min) / float(divisions)
    try:
        quantized_index = round(float(weekly_per_capita) / delta, 0)  # no info for this county for the desired date
    except:
        quantized_index = 0

    if quantized_index >= divisions:
        quantized_per_capita = str(">" + str(range_max))
    else:
        quantized_per_capita = str(round(float(quantized_index * delta), 3)) + " to " + str(
            round(float((quantized_index + 1) * delta), 3))

    location_date_record.append(quantized_per_capita)


    location_date_record.append(change_confirm)

    location_date_record.append(change_confirm_per_1000)

    dataframe_list.append(location_date_record)

    if len(location_date_record) != 21:
        print("Len of record = ", len(location_date_record))
        break


    # get category_order_list
capita_order_list = []
for index in range(0,divisions):
      capita_order_list.append(str(round(float(range_min+index * delta),3)) + " to " + str(round(float(range_min+(index+1)*delta),3)))
capita_order_list.append(str(">"+str(range_max)))
# now create the header
header = ["FIPS","location","date", "Confirmed","Deaths","Weekly % Change", "New Deaths % Change"]

header.append("Current Week New Cases")
header.append("Last Week New Cases")

for i in range(2,len(interval_days)-1):
    header.append(str(i) + " Weeks Ago New Cases")

header.append("Current Week New Deaths")
header.append("Last Week New Deaths")
for i in range(2,len(interval_days)-1):
   header.append(str(i) + " Weeks Ago New Deaths")


header.append("quantized_color")
header.append("Cases Per 1000")
header.append("Population")
header.append("Quantized Per Capita")
header.append("Weekly Change in Confirmed")
header.append("Weekly Change in Confirmed Per 1000")
dfchange = pd.DataFrame(dataframe_list,columns = header) # this is the complete dataframe with 15 columns
# FIPS | location | date | Confirmed | Deaths | Change_Confirmed_% | Change_Deaths_% ! Current Week New Cases | Last Week New Cases
#2 Weeks Ago New Cases | 3 Weeks Ago New Cases |4 Weeks Ago New Cases | Current Week New Deaths | Last Week New Deaths
#2 Weeks Ago New Deaths | 3 Weeks Ago New Deaths |4 Weeks Ago New Deaths
#choose the columns you want for the plot

#OK now lets plot it:
import plotly as px  #.express as px
import pandas as pd
from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)
import plotly.express as px

fig = px.choropleth(dfchange, geojson=counties, locations='FIPS', color="Current Week New Cases", #'"quantized_color", #geojson=counties

                            color_continuous_scale="Reds", #Rainbow",#Viridis",
                          # category_orders= {"quantized_color":category_order_list},
                           #color_discrete_sequence = px.colors.sequential.Reds, #['#FFFFFF','#FFDFDF','#FFBFBF','#FF9F9F','#FFAFAF','#FF8F8F','#FF6F6f','#FF4F4f','#FF0000'],
                          range_color=(0, 700),  # the scale is max'd I don't know how to say ">700" maybe use a discrete scale
                           scope="usa",
                          # labels = False,
                           labels={"FIPS":"Location Index","Current Week New Cases":"Current Week New Cases"},#"quantized_color":"Current Week New Cases"},

                           #locationmode="USA-states",
                           hover_name = "location",


                          hover_data =["Weekly % Change","Current Week New Cases","Last Week New Cases","2 Weeks Ago New Cases","3 Weeks Ago New Cases"]

                          )
fig.update_layout(margin={"r":0,"t":25,"l":0,"b":0},



                  title_text = "<b>New Covid Cases this Week Ending "+ date_v + " by US County (Updated Daily)</b>",
       #           y = .9, yref = 'paper', yanchor = 'bottom', x = .5, xref='paper',xanchor = 'center',

                  geo = dict(
                             showcoastlines=False,
                             showcountries = True

                            )


                  )
fig.add_annotation(   y = .30, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<b>Hover, Scroll, & Zoom on<br>Large Screen to Explore County Data</b>"
                            # Novel Coronavirus (COVID-19) Cases, provided by JHU CSSE "
                              #  <a href='https://github.com/CSSEGISandData/COVID-19'></a> "
                      )
fig.add_annotation(   y = .25, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_per_capita.html'> Map New Weekly Cases per 1000 people</a> "
                      )

fig.add_annotation(   y = .215, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_change.html'> Map Change in Weekly Cases</a> "
                      )
fig.add_annotation(   y = .18, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_change_per_1000.html'> Map Change in Weekly Cases Per 1000</a> "
                      )
fig.add_annotation(   y = .145, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_deaths.html'> Map New Weekly Deaths</a> "
                      )
fig.add_annotation(   y = .11, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_per_capita_deaths.html'> Map New Weekly Deaths per 10000</a> "
                      )
fig.add_annotation(   y = .075, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_change_deaths.html'> Map Change in Weekly Deaths</a> "
                      )
fig.add_annotation(   y = .04, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_change_per_10000_deaths.html'> Map Change in Weekly Deaths/10000</a> "
                      )
fig.add_annotation(   y = .005, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "Data Provided by <a href='https://github.com/CSSEGISandData/COVID-19'> JHU CSSE</a> "
                      )
#fig.show()
fig.write_html("covid_county_weekly.html")

#now read the file back into a text string and put the google tracking scripts into the header
AddGoogleTracking("covid_county_weekly.html")



fig.write_html(str("./ArchivedMaps/covid_county_weekly_")+date_str+ ".html")
# now create map per capita *******************************************************************************************
#df_used = dfchange[["FIPS","Quantized Per Capita","Weekly % Change","Cases Per 1000","Population","Current Week New Cases","Last Week New Cases","2 Weeks Ago New Cases","3 Weeks Ago New Cases"]]
fig = px.choropleth(dfchange, geojson=counties, locations='FIPS', color="Cases Per 1000", #geojson=countiesCases Per Capita

                          color_continuous_scale="Reds", #Rainbow",#Viridis",
                         #  category_orders= {"Quantized Per Capita":capita_order_list},
                          # color_discrete_sequence = px.colors.sequential.Reds, #['#FFFFFF','#FFDFDF','#FFBFBF','#FF9F9F','#FFAFAF','#FF8F8F','#FF6F6f','#FF4F4f','#FF0000'],
                        range_color=(0, 4),  # the scale is max'd I don't know how to say ">700" maybe use a discrete scale
                           scope="usa",
                          # labels = False,
                           labels={"FIPS":"Location Index","Cases Per 1000":"Weekly New Cases Per 1000"},

                           #locationmode="USA-states",
                           hover_name = "location",


                          hover_data =["Weekly % Change","Cases Per 1000","Population","Current Week New Cases","Last Week New Cases","2 Weeks Ago New Cases","3 Weeks Ago New Cases"]

                          )
fig.update_layout(margin={"r":0,"t":25,"l":0,"b":0},



                  title_text = "<b>New Covid Cases Per 1000 People in County this Week Ending "+ date_v + "(Updated Daily)</b>",
       #           y = .9, yref = 'paper', yanchor = 'bottom', x = .5, xref='paper',xanchor = 'center',

                  geo = dict(
                             showcoastlines=False,
                             showcountries = True

                            )


                  )
fig.add_annotation(   y = .30, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<b>Hover, Scroll, & Zoom on<br>Large Screen to Explore County Data</b>"
                            # Novel Coronavirus (COVID-19) Cases, provided by JHU CSSE "
                              #  <a href='https://github.com/CSSEGISandData/COVID-19'></a> "
                      )
fig.add_annotation(   y = .25, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly.html'> Map New Weekly Cases</a> "
                      )
fig.add_annotation(   y = .215, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_change.html'> Map Change in Weekly Cases</a> "
                      )
fig.add_annotation(   y = .18, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_change_per_1000.html'> Map Change in Weekly Cases Per 1000</a> "
                      )

fig.add_annotation(   y = .145, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_deaths.html'> Map New Weekly Deaths</a> "
                      )
fig.add_annotation(   y = .11, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_per_capita_deaths.html'> Map New Weekly Deaths per 10000</a> "
                      )
fig.add_annotation(   y = .075, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_change_deaths.html'> Map Change in Weekly Deaths</a> "
                      )
fig.add_annotation(   y = .04, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_change_per_10000_deaths.html'> Map Change in Weekly Deaths/10000</a> "
                      )
fig.add_annotation(   y = .005, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "Data Provided by <a href='https://github.com/CSSEGISandData/COVID-19'> JHU CSSE</a> "
                      )

#fig.show()
fig.write_html("covid_county_weekly_per_capita.html")
#now read the file back into a text string and put the google tracking scripts into the header
AddGoogleTracking("covid_county_weekly_per_capita.html")
fig.write_html(str("./ArchivedMaps/covid_county_weekly_per_capita_")+date_str+ ".html")
# now create map for weekly change *******************************************************************************************
#df_used = dfchange[["FIPS","Quantized Per Capita","Weekly % Change","Cases Per 1000","Population","Current Week New Cases","Last Week New Cases","2 Weeks Ago New Cases","3 Weeks Ago New Cases"]]
fig = px.choropleth(dfchange, geojson=counties, locations='FIPS', color="Weekly Change in Confirmed", #geojson=countiesCases Per Capita

                           color_continuous_scale="Picnic", #Rainbow",#Viridis",
                           #category_orders= {"Quantized Per Capita":capita_order_list},
                           #color_discrete_sequence = px.colors.sequential.Reds, #['#FFFFFF','#FFDFDF','#FFBFBF','#FF9F9F','#FFAFAF','#FF8F8F','#FF6F6f','#FF4F4f','#FF0000'],
                           range_color=(-300, 300),  # the scale is max'd I don't know how to say ">700" maybe use a discrete scale
                           scope="usa",
                          # labels = False,
                           labels={"FIPS":"Location Index","Weekly Change in Confirmed":"Weekly Change in Cases"},

                           #locationmode="USA-states",
                           hover_name = "location",


                          hover_data =["Weekly Change in Confirmed","Weekly % Change","Current Week New Cases","Last Week New Cases","2 Weeks Ago New Cases","3 Weeks Ago New Cases"]

                          )
fig.update_layout(margin={"r":0,"t":25,"l":0,"b":0},



                  title_text = "<b>Weekly Change in New Covid Cases for Week Ending "+ date_v + " by US County (Updated Daily)</b>",
       #           y = .9, yref = 'paper', yanchor = 'bottom', x = .5, xref='paper',xanchor = 'center',

                  geo = dict(
                             showcoastlines=False,
                             showcountries = True

                            )


                  )
fig.add_annotation(   y = .30, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<b>Hover, Scroll, & Zoom on<br>Large Screen to Explore County Data</b>"
                            # Novel Coronavirus (COVID-19) Cases, provided by JHU CSSE "
                              #  <a href='https://github.com/CSSEGISandData/COVID-19'></a> "
                      )
fig.add_annotation(   y = .25, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly.html'> Map New Weekly Cases</a> "
                      )
fig.add_annotation(   y = .215, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_per_capita.html'> Map New Weekly Cases per 1000</a> "
                      )
fig.add_annotation(   y = .18, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_change_per_1000.html'> Map Change in Weekly Cases per 1000</a> "
                      )
fig.add_annotation(   y = .145, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_deaths.html'> Map New Weekly Deaths</a> "
                      )
fig.add_annotation(   y = .11, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_per_capita_deaths.html'> Map New Weekly Deaths per 10000</a> "
                      )
fig.add_annotation(   y = .075, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_change_deaths.html'> Map Change in Weekly Deaths</a> "
                      )
fig.add_annotation(   y = .04, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_change_per_10000_deaths.html'> Map Change in Weekly Deaths/10000</a> "
                      )
fig.add_annotation(   y = .005, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "Data Provided by <a href='https://github.com/CSSEGISandData/COVID-19'> JHU CSSE</a> "
                      )
#fig.show()
fig.write_html("covid_county_weekly_change.html")
AddGoogleTracking("covid_county_weekly_change.html")
fig.write_html(str("./ArchivedMaps/covid_county_weekly_change_")+date_str+ ".html")
# now create map for weekly change per 1000  *******************************************************************************************
#df_used = dfchange[["FIPS","Quantized Per Capita","Weekly % Change","Cases Per 1000","Population","Current Week New Cases","Last Week New Cases","2 Weeks Ago New Cases","3 Weeks Ago New Cases"]]
fig = px.choropleth(dfchange, geojson=counties, locations='FIPS', color="Weekly Change in Confirmed Per 1000", #geojson=countiesCases Per Capita

                           color_continuous_scale="Picnic", #Rainbow",#Viridis",
                           #category_orders= {"Quantized Per Capita":capita_order_list},
                           #color_discrete_sequence = px.colors.sequential.Reds, #['#FFFFFF','#FFDFDF','#FFBFBF','#FF9F9F','#FFAFAF','#FF8F8F','#FF6F6f','#FF4F4f','#FF0000'],
                           range_color=(-4, 4),  # the scale is max'd I don't know how to say ">700" maybe use a discrete scale
                           scope="usa",
                          # labels = False,
                           labels={"FIPS":"Location Index","Weekly Change in Confirmed Per 1000":"Weekly Change Cases/1000"},

                           #locationmode="USA-states",
                           hover_name = "location",


                          hover_data =["Weekly Change in Confirmed Per 1000","Population","Weekly % Change","Current Week New Cases","Last Week New Cases","2 Weeks Ago New Cases","3 Weeks Ago New Cases"]

                          )
fig.update_layout(margin={"r":0,"t":25,"l":0,"b":0},



                  title_text = "<b>Weekly Change in New Covid Cases Per 1000 People in County for Week Ending "+ date_v + "</b>",
       #           y = .9, yref = 'paper', yanchor = 'bottom', x = .5, xref='paper',xanchor = 'center',

                  geo = dict(
                             showcoastlines=False,
                             showcountries = True

                            )


                  )
fig.add_annotation(   y = .30, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<b>Hover, Scroll, & Zoom on<br>Large Screen to Explore County Data</b>"
                            # Novel Coronavirus (COVID-19) Cases, provided by JHU CSSE "
                              #  <a href='https://github.com/CSSEGISandData/COVID-19'></a> "
                      )
fig.add_annotation(   y = .25, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly.html'> Map New Weekly Cases</a> "
                      )
fig.add_annotation(   y = .215, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_per_capita.html'> Map New Weekly Cases per 1000</a> "
                      )
fig.add_annotation(   y = .18, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_change.html'> Map Change in Weekly Cases</a> "

                    )

fig.add_annotation(   y = .145, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_deaths.html'> Map New Weekly Deaths</a> "
                      )
fig.add_annotation(   y = .11, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_per_capita_deaths.html'> Map New Weekly Deaths per 10000</a> "
                      )
fig.add_annotation(   y = .075, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_change_deaths.html'> Map Change in Weekly Deaths</a> "
                      )
fig.add_annotation(   y = .04, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "<a href='https://www.glutenfreeyouandme.com/covid/covid_county_weekly_change_per_10000_deaths.html'> Map Change in Weekly Deaths/10000</a> "
                      )
fig.add_annotation(   y = .005, yref = 'paper', yanchor = 'bottom', x = .895, xref='paper',xanchor = 'center', showarrow = False,
                      text = "Data Provided by <a href='https://github.com/CSSEGISandData/COVID-19'> JHU CSSE</a> "
                      )
#fig.show()
fig.write_html("covid_county_weekly_change_per_1000.html")
AddGoogleTracking("covid_county_weekly_change_per_1000.html")

fig.write_html(str("./ArchivedMaps/covid_county_weekly_change_per_1000_")+date_str+ ".html")