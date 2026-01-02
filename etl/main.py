import functions_framework
import pandas as pd
from google.cloud import bigquery, storage
import os
import json

@functions_framework.cloud_event
def etl_handler(cloud_event):
    data = json.loads(cloud_event.data.decode('utf-8'))
    bucket_name = data['bucket']
    file_name = data['name']
    
    # Extract
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    df = pd.read_csv(f'gs://{bucket_name}/{file_name}')
    
    # Transform
    df['age_group'] = pd.cut(df['age'], bins=[0, 18, 35, 60, 100], labels=['minor', 'young_adult', 'adult', 'senior'])
    
    # Load (idempotent: truncate + append)
    bq_client = bigquery.Client()
    table_id = f"{os.environ['GOOGLE_CLOUD_PROJECT']}.{os.environ['BQ_DATASET']}.{os.environ['BQ_TABLE']}"
    job = bq_client.load_table_from_dataframe(df, table_id, write_disposition='WRITE_TRUNCATE')
    job.result()
    print(f"Loaded {job.output_rows} rows to {table_id}")
