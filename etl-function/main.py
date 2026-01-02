""" ETL Cloud Function - Process CSV and loads into Bigquery"""
import os
from datetime import datetime
import pandas as pd
from google.cloud import storage,bigquery
import functions_framework


PROJECT_ID=os.environ.get('PROJECT_ID')
DATASET_ID=os.environ.get('DATASET_ID')
TABLE_ID=os.environ.get('TABLE_ID')


@functions_framework.cloud_event
def process_file(cloud_event):
    """triggered by file upload to GCS"""
    try:
        ##get file information
        data=cloud_event.data
        bucket_name=data['bucket']
        file_name=data['name']

        print(f"processing: gs://{bucket_name}/{file_name}")

        #only process csv files
        if not file_name.endswith('.csv'):
            print(f"skipping non csv file :{file_name}")
            return
        #Extract :Read from GCS
        df=extract_from_gcs(bucket_name,file_name)

        #transform processed data
        df=transform_data(df)

        #load :write to bigquery
        load_to_bigquery(df)

        print(f"Successfully processed {len(df)} rows")
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    

def extract_from_gcs(bucket_name,file_name):
    """Extract csv from google cloud storage"""
    print("EXTRACT: Reading from GCS...")


    storage_client=storage.client()
    bucket=storage_client.bucket(bucket_name)
    blob=bucket.blob(file_name)
    csv_data=blob.download_as_text()


    from io import StringIO
    df=pd.read_csv(StringIO(csv_data))

    print(f"Extract: Loaded {len(df)} rows")
    return df

def transform_data(df):
    """Transform and validate data"""
    print("Transform: Processing data")

    #calculate Total
    df['total']=df['quantity']* df['price']

    #add processing timestamp
    df['processed_at']=datetime.now(datetime.timezone.utc)

    #convert date to proper format

    df['date']=pd.to_datetime(df['date'])

    #validate required fileds

    required_cols=['transaction_id','date','product','quantity','price']
    
    for col in required_cols:
        if df[col].isnull().any():
            raise ValueError(f" Missing Values in {col}")
        
    print(f"TRANSFORM: Processed {len(df)} rows")
    return df


def load_to_bigquery(df):
    """Load data to bigquery"""
    print("LOAD: Writing to Bigquery")

    client=bigquery.client()
    table_id=f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}",
     
    job_config=bigquery.LoadJobConfig(
        write_desposition="WRITE_APPEND",
    )

    job=client.load_table_from_dataframe(
        df,table_id,job_config=job_config
    )
    job.result()

    print(f"LOAD: Loaded {len(df)} rows to {table_id}")