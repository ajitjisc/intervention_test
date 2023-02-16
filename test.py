import os
import tempfile
import logging
import tempfile
import pandas as pd
import requests
import datetime
import io
import shutil


def get_interventions(lrwid):
    today = datetime.datetime.today().strftime('%m/%d/%Y')
    url = f"https://api-testing.datax.jisc.ac.uk/intervention/export/{lrwid}?startDate=12%2F01%2F2019&endDate={today}&Id={lrwid}"
    username = "service"
    password = "xvu7Qg84uHuwZkAF"
    response = requests.get(url,auth=(username, password))
    with tempfile.NamedTemporaryFile(mode='w', delete
    = False) as f:
        f.write(response.text)
        temp_file_name = f.name
    return pd.read_csv(temp_file_name)
    
# A list of dictionaries, each containing information about an institution
institutions = [
        {
            "lrwid": "5fd89228fe8fcf04ac1a5094",
            "institution_name": "cwtest",
        }
        
    ]
# Loop through each institution in the list
for instituion in institutions:
     # Extract the LRWID and institution name from the dictionary
    lwrid= instituion["lrwid"]
    institution_name = instituion["institution_name"]
    
    # print(lwrid)
    # print(institution_name)
    # Get the interventions data for the current institution
    df = get_interventions(lwrid)
    # convert 'Created' column in df to datetime format
    df['Created'] = pd.to_datetime(df['Created'], format='%m/%d/%Y')

    # checking for empty data frame that occurs due to invalid lrwid
    if len(df.columns) < 2:
        print('invalid lwrid')
        continue
    
    # Create a filename 
    filename = f"{institution_name}_interventions.tsv"

    # Create a location for the file based on the institution name
    # AC1: A tsv file saved in a secure place that only a particular institution has access to
    # location = f"C:/Users/ajit.chandran/Desktop/intervention_test/{institution_name}/reports"
    location = f"/la-data/{institution_name}/reports"
    # if the report path is not exist, create a new one
    if not os.path.exists(location):
        os.makedirs(location)

    # change the directory to the instituion report location
    os.chdir(location)

    # AC2: The file has the previous day’s interventions in it
    try:
        # read existing file
        existing_df = pd.read_csv(filename,sep='\t', encoding='utf-8')
        existing_df['Created'] = pd.to_datetime(existing_df['Created'], format='%Y/%m/%d')

         # find the latest date in the existing data
        latest_date = existing_df['Created'].max()
    
        # filter new data based on the latest date in the existing data
        new_data = df[df['Created'] > latest_date]

        if not new_data.empty:
            # append new data to existing data
            append_dataframe = pd.concat([existing_df, new_data], ignore_index=True)
            append_dataframe.to_csv(filename, sep="\t", encoding="utf-8", index=False)
            print(f"New dataframe:{append_dataframe}")
        else:
            # no new data, do not update file
            print("No new rows to append.")
    except Exception as e:
        # if file does not exist, create a new one
        print(f"File was not found, creating new one: {e}")
        df.to_csv(filename,sep="\t", encoding="utf-8", index=False)
      
  
