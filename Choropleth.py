#Using Python 3.7
#with packages below
import plotly.express as px
import pandas as pd
from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

import pandas as pd
#df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
#                   dtype={"fips": str})
df = pd.read_csv("May_14_totals.csv",
                  dtype={"FIPS": str})

import plotly.express as px

fig = px.choropleth(df, geojson=counties, locations='FIPS', color='Confirmed', #geojson=counties

                           color_continuous_scale="Rainbow",#Viridis",
                           range_color=(0, 3000),
                           scope="usa",
                          # labels = False,
                           labels={"FIPS":"Location Index",'Confirmed':'Confirmed Cases'},

                           #locationmode="USA-states",
                           hover_name = "county-state",


                           # hover_data =["Confirmed"],

                          )
fig.update_layout(margin={"r":0,"t":25,"l":0,"b":0},

                  title_text = "Total Confirmed Cases 5-14-2020",

                  geo = dict(
                             showcoastlines=False,
                             showcountries = True

                            )


                  )

fig.show()
