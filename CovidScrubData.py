import glob
import csv
from csv import reader
email_list = []
email_pair_list = []


def save_csv_file_from_list(data, filename):
    file = open(filename, 'w+', newline='')

    # writing the data into the file
    with file:
        write = csv.writer(file)
        write.writerows(data)

    return


list_of_files = glob.glob('JHUCovidData/*.csv')
county_date_list =[]
header = ["FIPS","location","file_date","Confirmed","Deaths"]
county_date_list.append(header)
Country_Region = 3
FIPS = 0
County = 1
State = 2
Last_Update = 4
Confirmed = 7
Deaths = 8
Combined_Key = 11
for file_name in list_of_files:
    # get date from file_name
    date_file = file_name[file_name.find('\\') + 2:file_name.find(".csv")]
    with open(file_name,'r') as csvfile:
        list_of_rows = reader(csvfile)
        list_of_records =list(list_of_rows)
        for countyDate in list_of_records[1:]:
            #is this a record we want: US with a FIPS number


            if str(countyDate[Country_Region]).find('US') != -1 and  len(str(countyDate[Country_Region])) < 3:
                if len(str(countyDate[FIPS])) > 3:  # Need a Fips number
                    if int(countyDate[FIPS]) > 1000:
                        if len(str(countyDate[FIPS])) == 4:
                            fips = "0" + str(countyDate[FIPS])# need to add a leading zero
                        else:
                         fips = str(countyDate[FIPS])
                       # date = str(countyDate[Last_Update])[0:str(countyDate[Last_Update]).find(" ")]
                        city_state = str(countyDate[County])+ " County, " + str(countyDate[State])
                        record = [str(fips),city_state,date_file,countyDate[Confirmed],countyDate[Deaths]]
                        county_date_list.append(record)
    csvfile.close()
# now output the file as a CSV file
save_csv_file_from_list(county_date_list, "all_days.csv")