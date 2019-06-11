import subprocess
import sys

def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])
def opening_message():
    install_answer=input("Hello! This program allows you to look closely at building permits in Seattle.\nBy running this program, you will generate a geogrpahical heatmap showing you\nwhere the permits you are interested in are,\nand a pie chart giving you the status of the permits.\nFor this to work, you will need to install the python libraries gmplot and plotly\nHave you already installed these?\nSaying no will start installation of these libraries which may take a moment.\n(1) Yes\n(2) No\nPlease type 1 or 2\n")
    if install_answer == str(1):
        print("Ok then! Let me ask you some questions\nabout what building permits you are interested in.\n\n")
    else:
        if install_answer == str(2):
            install('gmplot')
            install('plotly')
            print("Ok, everything is installed! Now let me ask you some questions about what building permits you are interested in.\n\n")
        else:
            print("I did not understand that, please type 1 or 2")
            return get_user_input()

import pandas as pd
import gmplot
import requests
import webbrowser
pd.options.mode.chained_assignment = None
import plotly
import plotly.plotly as py


data_input = {}


dictionary_of_possible_inputs = {'permit_type_1':'Building', 'permit_type_2': 'Demolition', 'permit_class_1': 'Non-Residential', 'permit_class_2': 'Residential'}
def get_user_input():
    user_perm_input = input('What kind of permit are we talking about?\n(1) Building\n(2) Demolition\nPlease type 1 or 2\n')
    if user_perm_input == str(1):
        data_input['input1'] ='Building'
    else:
        if user_perm_input == str(2):
            data_input['input1'] ='Demolition'
        else:
            print("I did not understand that, please type 1 or 2")
            return get_user_input()
    
    user_perm_class_input = input('Do you want to know about residential or non-residential buildings?\n(1) Residential\n(2) Non-Residential\nPlease type 1 or 2\n')
    if user_perm_class_input == str(1):
        data_input['input2'] ='Residential'
    else:
        if user_perm_class_input == str(2):
            data_input['input2'] ='Non-Residential'
        else:
            print("I did not understand that, please type 1 or 2")
            return get_user_input()
#     date_input==user_date_input
    user_date_input = input('What year are you looking for?\nTechnically any year after 1986 works, but the \ndataset has more data from 2005 onward,\nwith the most data being after 2010')

    data_input['date']=user_date_input
    # print("Alright, thanks for the input. Hold on a moment while your data is retrieved...")

def request_function():
    base = 'https://data.seattle.gov/resource/k44w-2dcq.json?$limit=500000'
    permit = '&permittype='
    permit_input = data_input['input1']
    data_input['date_input'] = data_input['date']
    permit_class = '&permitclassmapped='
    permit_class_input=data_input['input2']
    response = requests.get(base+permit+permit_input+permit_class+permit_class_input)
    print("Got your data! Now building you a heatmap and a pie chart...")
    return response
# get_user_input()
# date_input


def build_heatmap(response):
    variable=response
    building_data=variable.json()
    Seattle_frame = pd.DataFrame.from_dict(building_data)
    dropped_frame = Seattle_frame.drop(['completeddate','contractorcompanyname','description', 'estprojectcost', 'expiresdate', 'housingunits', 'housingunitsadded', 'housingunitsremoved', 'issueddate', 'originalcity', 'originalstate', 'originalzip', 'permitnum', 'permittypedesc', 'link', 'location_2', 'location_2_address', 'location_2_city', 'location_2_state', 'location_2_zip'], 1)
    dropped_NAN_frame=dropped_frame.dropna()
    dropped_NAN_frame['applieddate']=dropped_NAN_frame['applieddate'].str[:4]

    dropped_date=dropped_NAN_frame[dropped_NAN_frame.applieddate == str(data_input['date_input'])]
    dropped_date

    dropped_date['latitude'] = dropped_date['latitude'].astype(float)
    dropped_date['longitude'] = dropped_date['longitude'].astype(float)
    Seattle_lat = dropped_date['latitude']
    Seattle_lon = dropped_date['longitude']

    gmap_seattle= gmplot.GoogleMapPlotter(47.6062, -122.3321, 10)

    gmap_seattle.heatmap(Seattle_lat, Seattle_lon)
    gmap_seattle.draw('seattle_heatmap'+"_"+data_input['input1']+"_"+data_input['input2']+"_"+data_input['date_input']+'.html')
    print("Your heatmap is built!")
    webbrowser.open('seattle_heatmap'+"_"+data_input['input1']+"_"+data_input['input2']+"_"+data_input['date_input']+'.html')
    return dropped_date




def create_pie_status(dictionary):
    fig = {
        'data': [
            {
                'labels': list(dictionary.keys()),
                'values': list(dictionary.values()),
                'type': 'pie',
            },
        ],
        'layout': {'title': 'Status Of '+data_input['input2']+'<br>Building Permits for<br>'+data_input['input1']+' in Seattle, Wa for '+data_input['date_input'],
                   'showlegend': True}
    }
    # py.iplot(fig, filename='pie_chart_subplots')
    plotly.offline.plot(fig, filename='seattle_pichart'+"_"+data_input['input1']+"_"+data_input['input2']+"_"+data_input['date_input']+'currentstatus'+'.html')
    print("Your pie chart is built!")



def full_function():
    get_user_input()
    var=build_heatmap(request_function())
    dropped_NAN_frame_two=var

    list_of_statuses =['Completed',
    'Issued',
    'Additional Info Requested',
    'Canceled',
    'Closed',
    'Corrections Required',
    'Expired',
    'Withdrawn',
    'Application Completed',
    'Reviews In Process',
    'Scheduled and Submitted',
    'Reviews Completed',
    'Scheduled',
    'Ready for Issuance',
    'Ready for Intake',
    'Corrections Submitted',
    'Active',
    'Approved to Occupy',
    'In Process',
    'Initiated',
    'Inspections Completed',
    'Reviews In Process',
    ]
    dict_of_status_count={}

    for string in list_of_statuses:
        dict_of_status_count[string]=dropped_NAN_frame_two['statuscurrent'].str.count(string).sum()

    create_pie_status(dict_of_status_count)

if __name__ == "__main__":
    opening_message()
    full_function()