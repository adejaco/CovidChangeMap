
import csv
from csv import reader


def save_csv_file_from_list(data, filename):
    file = open(filename, 'w+', newline='')

    # writing the data into the file
    with file:
        write = csv.writer(file)
        write.writerows(data)

    return

list_of_fips = []
#and the most current date
with open("all_days.csv", 'r') as csvfile:
    list_of_rows = reader(csvfile)
    list_of_records = list(list_of_rows)
    Fip_County = {}
    for fips in list_of_records[1:]:
        if fips[0] not in list_of_fips:
            Fip_County[fips[1]] = fips[0]  # build dictionary of county name to fips number


#Create a FIPS county csv file : FIPS,location,census population 2010, estimated population 2019
list_of_counties = []
header = ["FIPS","location","census population 2010", "estimated population 2019"]
list_of_counties.append(header)
with open("County_population_estimates.csv", 'r') as csvfile:
    list_of_rows = reader(csvfile)
    list_of_records = list(list_of_rows)
    for county in list_of_records[1:]:
        location = county[1] +", "+ county[0]


        try:
                fips = Fip_County[location]
                fip_population = [fips,location,county[2],county[3]]
                list_of_counties.append(fip_population)
        except:

                print("county names don't match")
csvfile.close()
            #look up population by county name
save_csv_file_from_list(list_of_counties, "fip_county_population.csv")       #create a datetime.date

