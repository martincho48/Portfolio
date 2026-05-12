# Databricks notebook source
# MAGIC %md
# MAGIC #Inputs

# COMMAND ----------

folder_name = 'landing_folder'
file_kind = '.csv'
file_string_upcoming = 'df_upcoming'
file_string_credits = 'df_credits'

# COMMAND ----------

# MAGIC %md
# MAGIC #Read CSV files

# COMMAND ----------

def read_latest_file(folder_name: str, search_string: str):
    # Directory path
    directory_path = f'/mnt/container/{folder_name}/'

    # Check if the directory exists using Spark's file system
    fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
    path = spark._jvm.org.apache.hadoop.fs.Path(directory_path)

    if not fs.exists(path):
        raise FileNotFoundError(f"Directory {directory_path} not found.")
    
    # List all files in the directory
    files = fs.listStatus(path)
    
    # Filter to only keep .csv files that contain the search_string in the filename
    csv_files = [
        file.getPath().toString() 
        for file in files 
        if file.getPath().toString().endswith(file_kind) and search_string in file.getPath().toString()
    ]
    
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found with the string '{search_string}' in the filename.")
    
    # Get the latest file based on the timestamp in the file path
    latest_file = max(csv_files, key=lambda x: fs.getFileStatus(spark._jvm.org.apache.hadoop.fs.Path(x)).getModificationTime())

    # Return the file name
    return latest_file



# COMMAND ----------

# Get the latest file from the directory
latest_file_upcoming = read_latest_file(folder_name, file_string_upcoming)
latest_file_credits = read_latest_file(folder_name, file_string_credits)
print(latest_file_upcoming)
print(latest_file_credits)

# COMMAND ----------

df_upcoming = (spark
              .read
              .option("escape", "\"")
              .option("header", "true")
              .csv(latest_file_upcoming)
)

df_upcoming.display()

# COMMAND ----------

df_credits = (spark
              .read
              .option("escape", "\"")
              .option("header", "true")
              .csv(latest_file_credits)
)

df_credits.display()

# COMMAND ----------

# MAGIC %md
# MAGIC #Parse-json

# COMMAND ----------

# df = df_credits.select('crew').limit(3)
# df.display()

# COMMAND ----------

# # from pyspark.sql.functions import from_json, col
# from pyspark.sql.types import StringType, StructType, StructField

# # Define schema based on the structure of the JSON
# schema = StructType([
#     StructField("Director", StringType(), True),
# ])

# # Parse the JSON column ('crew') into structured columns
# df_parsed = df.withColumn("parsed_crew", from_json(col("crew").cast(StringType()), schema))


# # Add the Director column to df_parsed
# df_parsed = df_parsed.withColumn("Director", col("parsed_crew.Director"))

# # Show the results
# df_parsed.display()

# COMMAND ----------

# MAGIC %md
# MAGIC #Define functions for parsing

# COMMAND ----------

from pyspark.sql.functions import regexp_extract

def add_col_from_dict(df, column, pattern, new_col_name):

    # Use f-string to dynamically insert the variable into the regex
    df = df.withColumn(new_col_name, regexp_extract(column, fr'{pattern}([^"]+)"', 1))

    return df

# COMMAND ----------

from pyspark.sql.functions import from_json, col
from pyspark.sql.types import ArrayType, StringType

def parse_into_array(df,source_col_name, new_col_name):
    # Define the schema for the JSON array (array of strings)
    array_schema = ArrayType(StringType())

    # Parse the JSON strings into actual arrays
    df = df.withColumn(new_col_name, from_json(col(source_col_name), array_schema))

    return df

# COMMAND ----------

def extract_two_values(df, source_col_name, new_col_name1, new_col_name2):
    # Extract the first and second elements from the array
    df = df.withColumn(new_col_name1, col(source_col_name)[0]) \
                        .withColumn(new_col_name2, col(source_col_name)[1])
    return df

# COMMAND ----------

def extract_one_value(df, source_col_name, new_col_name):
    # Extract the first and second elements from the array
    df = df.withColumn(new_col_name, col(source_col_name)[0])
    return df

# COMMAND ----------

# MAGIC %md
# MAGIC #Run functions

# COMMAND ----------

# MAGIC %md
# MAGIC ####Add cols using Regex

# COMMAND ----------

df_cred = add_col_from_dict(df=df_credits, column='crew', pattern='Director":"', new_col_name='director')
df_cred = add_col_from_dict(df=df_cred, column='crew', pattern='Producer":"', new_col_name='producer')
df_cred = add_col_from_dict(df=df_cred, column='crew', pattern='Director of Photography":"', new_col_name='camera')
df_cred = add_col_from_dict(df=df_cred, column='crew', pattern='Original Music Composer":"', new_col_name='music_composer')
df_cred = add_col_from_dict(df=df_cred, column='crew', pattern='Screenplay":"', new_col_name='screenplay')
df_cred.display()

# COMMAND ----------

# from pyspark.sql.functions import from_json, col
# from pyspark.sql.types import ArrayType, StringType


# # Define the schema for the JSON array (array of strings)
# array_schema = ArrayType(StringType())

# # Parse the JSON strings into actual arrays
# df_cred = df_cred.withColumn("genres", from_json(col("genres"), array_schema))

# # Extract the first and second elements from the array
# df_cred = df_cred.withColumn("first_genre", col("genres")[0]) \
#                      .withColumn("second_genre", col("genres")[1])

# # Show the result
# df_cred.display()


# COMMAND ----------

# MAGIC %md
# MAGIC ####Parse cols

# COMMAND ----------

df_cred = parse_into_array(df = df_cred,
                    source_col_name = 'genres', 
                    new_col_name = 'genres'
                    )

df_cred = parse_into_array(df = df_cred,
                    source_col_name = 'cast-name', 
                    new_col_name = 'cast-name'
                    )


df_cred = parse_into_array(df = df_cred,
                    source_col_name = 'production_companies', 
                    new_col_name = 'production_companies'
                    )

df_cred = parse_into_array(df = df_cred,
                    source_col_name = 'production_countries', 
                    new_col_name = 'production_countries'
                    )


df_cred = parse_into_array(df = df_cred,
                    source_col_name = 'spoken_languages', 
                    new_col_name = 'spoken_languages'
                    )

# COMMAND ----------

df_cred.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ######Add cols

# COMMAND ----------

df_cred = extract_two_values(df = df_cred, 
                        source_col_name = 'cast-name', 
                        new_col_name1 = 'actor1', 
                        new_col_name2 = 'actor2'
                        )

df_cred = extract_one_value(df = df_cred, 
                        source_col_name = 'genres', 
                        new_col_name = 'genre', 
                        )

df_cred = extract_one_value(df = df_cred, 
                        source_col_name = 'production_companies', 
                        new_col_name = 'production_company', 
                        )

df_cred = extract_one_value(df = df_cred, 
                        source_col_name = 'production_countries', 
                        new_col_name = 'production_country', 
                        )

df_cred = extract_one_value(df = df_cred, 
                        source_col_name = 'spoken_languages', 
                        new_col_name = 'spoken_language', 
                        )

# COMMAND ----------

df_cred.display()

# COMMAND ----------

# MAGIC %md
# MAGIC #Drop cols

# COMMAND ----------

drop_list = ['cast-name', 'crew', 'genres', 'production_companies', 'production_countries', 'spoken_languages']

# COMMAND ----------

# Drop the specified columns in df_credits
df_cred = df_cred.drop(*drop_list)

df_cred.display()


# COMMAND ----------

# MAGIC %md
# MAGIC #Merge both dataframes

# COMMAND ----------

# Perform the merge (equivalent to join in Spark)
df_merged = df_upcoming.join(df_cred, on="id", how="inner")

# Show the first two rows
df_merged.display()


# COMMAND ----------

# MAGIC %md
# MAGIC #Treat empty items as null and check null values in cols

# COMMAND ----------

from pyspark.sql.functions import col, sum, when, lit
from pyspark.sql import Row

# Replace empty strings with null for all columns
for column in df_merged.columns:
    df_merged = df_merged.withColumn(
        column,
        when(col(column) == "", None).otherwise(col(column))
    )

# Show the updated DataFrame
df_merged.display()


# COMMAND ----------

# Calculate null counts for each column
null_counts = df_merged.select(
    [sum(when(col(c).isNull(), 1).otherwise(0)).alias(c) for c in df_merged.columns]
).collect()[0]

# Create a DataFrame showing column names and their null counts
result = spark.createDataFrame(
    [Row(column_name=c, null_count=null_counts[i]) for i, c in enumerate(df_merged.columns)]
)

# Sort the result by null_count in descending order and show
result.orderBy(col("null_count").desc()).display()


# COMMAND ----------

# MAGIC %md
# MAGIC #Drop useless cols

# COMMAND ----------

# MAGIC %md
# MAGIC ###Too many NaN

# COMMAND ----------

drop_list_nan = ['screenplay', 'music_composer', 'tagline', 'camera', 'backdrop_path' ]
drop_list_useless = ['genre_ids', 'video', 'adult','original_title', '_c0', 'poster_path' ]

drop_list_final = drop_list_nan + drop_list_useless

# Drop the specified columns in df_credits
df_merged = df_merged.drop(*drop_list_final)

df_merged.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Runtime > 50

# COMMAND ----------

# Filter the DataFrame 
df_merged = df_merged.filter(df_merged['runtime'] >= 50)
df_merged.display()

# COMMAND ----------

# MAGIC %md
# MAGIC #Remove duplicates = choose only distinct rows

# COMMAND ----------

# Retrieve distinct rows
df_merged = df_merged.distinct()

df_merged.display()

# COMMAND ----------

# MAGIC %md
# MAGIC #Set d-types

# COMMAND ----------

from pyspark.sql.functions import col

# Define columns and their target data types
columns_to_cast = {
    "id": "int",
    "popularity": "int",
    "vote_average": "int",
    "vote_count" : "int",
    "budget" : "int",
    "revenue" : "int",
    "runtime" : "int",
    "release_date" : "date"
}

# Cast all columns using a loop
for column, dtype in columns_to_cast.items():
    df_merged = df_merged.withColumn(column, col(column).cast(dtype))

df_merged.display()

# COMMAND ----------

# MAGIC %md
# MAGIC #Export results into ADLA like parquet

# COMMAND ----------

import datetime

# Save file as parquete in temporary folder 'tmp'
(df_merged.write 
  .mode("overwrite") 
  .option('compresion', 'snappy')          
  .parquet('/mnt/container/cleaned_data/tmp')
)

# Get the current timestamp and format it (e.g., 'YYYY-MM-DD_HH-MM-SS')
timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# List the files in the temporary folder 'tmp'
files = dbutils.fs.ls('/mnt/container/cleaned_data/tmp')
output_file = [x for x in files if x.name.startswith('part-')]

# Check if files matching the pattern exist
if output_file:
    # Move the first Parquet file to another folder 'cleaned_data' and rename it as well
    dbutils.fs.mv(output_file[0].path, f"/mnt/container/cleaned_data/output_{timestamp}.parquet")

    # Delete the 'tmp' folder and its contents
    dbutils.fs.rm("/mnt/container/cleaned_data/tmp", True)
else:
    print("No Parquet files found to move.")


# COMMAND ----------

# MAGIC %md
# MAGIC #Read the file from parquet

# COMMAND ----------

# # Define the output path where the Parquet files were saved
# file_name = f"output_2024-12-19_20-02-20.parquet"
# output_path = f"/mnt/container/cleaned_data/{file_name}"

# # Read the Parquet files into a DataFrame
# df_read = spark.read.parquet(output_path)
# df_read.display()
