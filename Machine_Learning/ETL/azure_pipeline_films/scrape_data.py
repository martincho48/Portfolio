# Databricks notebook source
# MAGIC %md
# MAGIC #Libraries

# COMMAND ----------

import requests
import os
import pandas as pd
from time import sleep
from datetime import datetime
from pathlib import Path
import json
import datetime


# COMMAND ----------

# MAGIC %md
# MAGIC #Inputs

# COMMAND ----------

scope_name = 'databricks_scope'
secrete_name_key = 'FilmDatabaseAPI-Key'
secrete_name_token = 'FilmDatabaseToken'

# Landing folder on the cloud
output_folder = "landing_folder"
output_file_name_upcoming = "df_upcoming"
output_file_name_credits = "df_credits"

# COMMAND ----------

# MAGIC %md
# MAGIC #Define functions

# COMMAND ----------

def api_upcoming(token, page, scope):

    # Get the credit_id 
    bearer_token = dbutils.secrets.get(scope=scope, key=token)


    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {bearer_token}"
    }

    params = {
        'language': 'en-US',
        #'append_to_response': 'credits',
        #'primary_release_date.gte':start_date,
        #'primary_release_date.lte': end_date,
        'page' : page
        }

    url = 'https://api.themoviedb.org/3/movie/upcoming'

    response = requests.get(url, headers=headers, params=params)

    return response

# COMMAND ----------

def api_credits(film_id, key, scope):

    # Get the credit_id and api_key from environment variables
    api_key = dbutils.secrets.get(scope=scope_name, key=secrete_name_key)

    url = f'https://api.themoviedb.org/3/movie/{film_id}?api_key={api_key}&append_to_response=credits'

    response = requests.get(url)

    return response

# COMMAND ----------

def api_credits_loop(input_list, key, scope, verbose=None):
    # Create an empty DataFrame with the required columns
    df = pd.DataFrame(columns=[
        'id',
        'budget',
        'production_companies', 
        'production_countries',
        'revenue', 
        'spoken_languages', 
        'genres', 
        'runtime',
        'tagline',
        'crew',
        'cast-name'
    ])

    counter_to_sleep = 0

    for item in input_list:
        try:
            response = api_credits(film_id=item, 
                                   key=key, 
                                   scope=scope
                                   )
            data = response.json()

        except Exception as err:
            print(f"An error occurred while processing the response: {err}")
            continue  # Skip to the next item

        # Create the crew dictionary and serialize it with double quotes
        crew_dict = {i.get('job'): i.get('name') for i in data['credits']['crew']}
        crew_dict_json = json.dumps(crew_dict)  # Convert to JSON string with double quotes

        # Create the new row, serializing lists to JSON with double quotes
        new_row = {
            'id': item,
            'budget': data['budget'],
            'production_companies': json.dumps([i.get('name') for i in data['production_companies']]),
            'production_countries': json.dumps([i.get('name') for i in data['production_countries']]),
            'spoken_languages': json.dumps([i.get('english_name') for i in data['spoken_languages']]),
            'genres': json.dumps([i.get('name') for i in data['genres']]),
            'revenue': data['revenue'],
            'runtime': data['runtime'],
            'tagline': data['tagline'],
            'crew': crew_dict_json,
            'cast-name': json.dumps([i.get('name') for i in data['credits']['cast']])
        }

        # Append the new row to the DataFrame
        df.loc[len(df)] = new_row

        counter_to_sleep += 1

        # Sleep after every certain number of iterations
        if counter_to_sleep % 40 == 0:
            sleep(1)

        if verbose:
            print(counter_to_sleep)
        
    return df


# COMMAND ----------

def api_upcoming_loop(token, scope):

    # We will first create an empty dataframe to store all the movie detail
    df = pd.DataFrame()

    page_counter = 1

    while True:

            response = api_upcoming(        token=token, 
                                            page=page_counter,
                                            scope=scope
                                            )
            

            temporary_df = pd.DataFrame(response.json()['results'])

            if not temporary_df.empty:
                    df = pd.concat([df, temporary_df],ignore_index=True)
        
            else:
                    break

            # Increment the page number and sleep counter
            page_counter += 1
            
            # Sleep after every certain number of iterations
            if page_counter%40==0: sleep(1)

            return df

# COMMAND ----------

# MAGIC %md
# MAGIC #Call functions

# COMMAND ----------

df_upcoming = api_upcoming_loop(token=secrete_name_token, scope=scope_name)
df_upcoming.head(2)

# COMMAND ----------

# Get the list of ids needed for API credits
id_list = df_upcoming['id'].to_list()
id_list[:5]

# COMMAND ----------

df_credits = api_credits_loop(      input_list = id_list,
                                    key=secrete_name_key,
                                    scope=scope_name,
                    )
df_credits.head(2)

# COMMAND ----------

# MAGIC %md
# MAGIC #Export CSVs

# COMMAND ----------

# Save DataFrames to Azure Data Lake
timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

df_upcoming.to_csv(f"/dbfs/mnt/container/{output_folder}/{output_file_name_upcoming}_{timestamp}.csv", index=False)
df_credits.to_csv(f"/dbfs/mnt/container/{output_folder}/{output_file_name_credits}_{timestamp}.csv", index=False)


