# Databricks notebook source
# MAGIC %md
# MAGIC #Import libraries

# COMMAND ----------

from pyspark.sql.functions import col
from pyspark.sql.functions import current_date, add_months, lit
import os

# COMMAND ----------

# MAGIC %md
# MAGIC #Inputs

# COMMAND ----------

# Define folder
folder_name = "cleaned_data"

# How many months in the past the filter should be applied
substract_months = 7

# COMMAND ----------

# Get today's date as a column
today_date_col = current_date()

# Subtract the specified number of months from today's date
two_months_ago = add_months(today_date_col, -substract_months)

# To get the value as a Python variable (collect the result)
filter_date = spark.range(1).select(two_months_ago.alias("substracted_date")).collect()[0]["substracted_date"]

# Print the result
print(filter_date)  # Outputs: The date 2 months ago


# COMMAND ----------

# MAGIC %md
# MAGIC #Get the latest file name in the dir

# COMMAND ----------

def read_latest_parquet_file(folder_name: str):
    # Directory path
    directory_path=f'/mnt/container/{folder_name}/'

    # Check if the directory exists using Spark's file system
    fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
    path = spark._jvm.org.apache.hadoop.fs.Path(directory_path)

    if not fs.exists(path):
        raise FileNotFoundError(f"Directory {directory_path} not found.")
    
    # List all files in the directory
    files = fs.listStatus(path)
    
    # Filter to only keep .parquet files
    parquet_files = [file.getPath().toString() for file in files if file.getPath().toString().endswith(".parquet")]
    
    if not parquet_files:
        raise FileNotFoundError("No Parquet files found in the specified directory.")

    # Get the latest file based on the timestamp in the file path
    latest_file = max(parquet_files, key=lambda x: fs.getFileStatus(spark._jvm.org.apache.hadoop.fs.Path(x)).getModificationTime())

    # Return the file name
    return latest_file

# COMMAND ----------

# MAGIC %md
# MAGIC #Read cleaned data

# COMMAND ----------

# Get the latest file from the directory
latest_file = read_latest_parquet_file(folder_name)

# Read the Parquet files into a DataFrame
df = spark.read.parquet(latest_file)
df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC # Filter cols

# COMMAND ----------

df1 = (df.filter((col("release_date") > filter_date))
        .select(col("title"),
                col("actor1"),
                col("actor2"), 
                col("genre"), 
                col("production_country"), 
                col("release_date"),
                col("overview")
                )
        .na.drop()
        )

df1.display()

# COMMAND ----------

# MAGIC %md
# MAGIC #Define functions

# COMMAND ----------

# Function to create a widget and return the selected value
def create_widget(df, col_name, filter_name):
    # Get distinct values from the column
    distinct_list = ["All"] + [row[col_name] for row in df.select(col_name).distinct().collect()]
    
    # Create the widget for filtering
    dbutils.widgets.dropdown(name=filter_name, 
                             defaultValue=distinct_list[0],  # Default to "All"
                             label=f"Filter by {col_name}:",
                             choices=distinct_list)
    
    # Get the selected value from the widget
    return dbutils.widgets.get(filter_name)



# COMMAND ----------

# Function to filter the DataFrame based on the selected widget value
def filter_df(df, col_name, filter_value):
    # Apply the filter if the selected value is not "All"
    if filter_value != "All":
        return df.filter(col(col_name) == filter_value)
    else:
        return df  # No filter applied if "All" is selected

# COMMAND ----------

# MAGIC %md
# MAGIC #Call functions

# COMMAND ----------

# MAGIC %md
# MAGIC ###Table with a widget

# COMMAND ----------

# Create and apply the second widget 
selected_genre = create_widget(df=df1, 
                               col_name="genre", 
                               filter_name="genre_filter"
                               )


final_filtered_df = filter_df(df=df1, 
                              col_name="genre", 
                              filter_value=selected_genre)


display(final_filtered_df)

# COMMAND ----------

sadadasd
