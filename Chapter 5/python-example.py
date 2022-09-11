"""
We can run this script to compare timings for loading the same file from GCS or
from local, testing schema auto-detection, or loading different formats. The load job will
automatically create or append to the table without deletion, so we can run this script
multiple times in succession to compare results. Running this script is free, but we will
be charged for the cost of the data storage once it’s in the table.
"""

# Load os library to manage targets and destinations
import os

# Load BigQuery from the Python GCP Library
from google.cloud import bigquery

# Load a performance timer (optional or comment out)
from timeit import default_timer as timer

# Specify your fully-qualified table name as you would in the UI

import_table = os.getenv('PROJECT_DATASET_TABLE')

# Choose the GCS bucket and file, or override it with a full gs:// URI
gcs_bucket = os.getenv('BUCKET_NAME')
gcs_file = os.getenv('BUCKET_FILE_NAME')

# gs://BKUCET_NAME/BUCKET_FILE_NAME OR local file ./LOCAL_FILE_NAME
location = ''
# location = f'gs://{gcs_bucket}/{gcs_file}'
# location = f'{os.getenv("LOCAL_FILE_NAME")'

# Load the references to the table for import

[project_name, dataset_name, table_name] = import_table.split('.')
client = bigquery.Client(project_name)
dataset = client.dataset(dataset_name)
table = dataset.table(table_name)

# Create the configuration and specify the schema
config = bigquery.LoadJobConfig()

config.schema = [
    bigquery.SchemaField("LastName", "STRING", "REQUIRED"),
    bigquery.SchemaField("FirstName", "STRING", "REQUIRED"),
    bigquery.SchemaField("GPA", "NUMERIC", "NULLABLE"),
    bigquery.SchemaField("EnrollmentDate", "DATE", "REQUIRED"),
    bigquery.SchemaField("ExpectedGraduationYear", "INTEGER", "REQUIRED")
]

# If you have a header row
config.skip_leading_rows = 1

# Comment to change import file type
config.source_format = bigquery.SourceFormat.CSV

# Uncomment and remove config.schema to autodetect schema
# config.autodetect = True

# Default to GCS
local = False
gcs_uri = ''

# Format the GCS URI
if (len(location) == 0):
    gcs_uri = "gs://{}/{}".format(gcs_bucket, gcs_file)
elif not (location.startswith('gs://')):
    local = True
else:
    gcs_uri = location

# Create the job definition
if (local):
    with open(location, "rb") as file:
        job = client.load_table_from_file(file, table, job_config=config)
else:
    job = client.load_table_from_uri(gcs_uri, table, job_config=config)

print ("Loading {} file {} into dataset {} as table {}...".format \
      (("local" if local else "GCS"), (location if local else gcs_uri),
        dataset_name, table_name))

# See if we have a timer
try:
    timer
    use_timer = True
except NameError:
    use_timer = False

if (use_timer):
    start = timer()

# Performs the load and waits for result
job.result()

if (use_timer):
    end = timer()
    result_time = " in {0:.4f}s".format(end-start)
else:
    result_time = ""

# Prints results
print("{} rows were loaded{}.".format(job.output_rows, result_time))
