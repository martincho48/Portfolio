# Databricks notebook source
# MAGIC %md
# MAGIC Mount the datalake with the container

# COMMAND ----------

# MAGIC %md
# MAGIC #Inputs

# COMMAND ----------

# Example variables for pipeline
source = 'wasbs://containermartin@datalakeportfoliomartin.blob.core.windows.net/'
mount_point = '/mnt/container'
scope = 'databricks_scope'
secret_name = 'secretdatalake'

# COMMAND ----------

# MAGIC %md
# MAGIC #Define functions

# COMMAND ----------

# MAGIC %md
# MAGIC ###Get all mounted points

# COMMAND ----------

def mounted_list(mount_point):

    # List all mounted paths
    mounted_paths = [mount.mountPoint for mount in dbutils.fs.mounts()]
    
    # Check if the specified mount_point is in the list of mounted paths
    return mount_point in mounted_paths


# COMMAND ----------

# MAGIC %md
# MAGIC ###Check if it is mounted-if not mount it

# COMMAND ----------

def ensure_mount(source, mount_point, scope, secret_name):
   
    try:
        if mounted_list(mount_point):
            print(f"The mount point '{mount_point}' is already mounted.")
        else:
            print(f"The mount point '{mount_point}' is not mounted. Proceeding to mount.")
            dbutils.fs.mount(
                source=source,
                mount_point=mount_point,
                # splits the source with @ and takes the second part of the split
                extra_configs={
                    f"fs.azure.account.key.{source.split('@')[1]}": dbutils.secrets.get(scope, secret_name) 
                }
            )
            print(f"Successfully mounted '{mount_point}'.")
    except Exception as e:
        print(f"Error occurred while mounting '{mount_point}': {e}")


# COMMAND ----------

# MAGIC %md
# MAGIC #Call the functions

# COMMAND ----------

# Ensure mount in the pipeline
ensure_mount(source, mount_point, scope, secret_name)

# Continue with the rest of the pipeline
print("Mount check complete. Proceeding with pipeline operations.")

