
import pandas as pd
from google.cloud import storage, bigquery

PROJECT_ID = "sonic-earth-476701-m1"
BUCKET_NAME = "sonic-earth-476701-m1-simple-de-raw"
SOURCE_OBJECT = "raw/data_raw_people.csv"
BQ_DATASET = "simple_de_demo"
BQ_TABLE = "people"

def extract_from_gcs():
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(SOURCE_OBJECT)
    data_bytes = blob.download_as_bytes()
    df = pd.read_csv(pd.io.common.BytesIO(data_bytes))
    return df

def transform(df: pd.DataFrame) -> pd.DataFrame:
    def age_group(age):
        if age < 18:
            return "minor"
        elif age < 30:
            return "young_adult"
        else:
            return "adult"
    df["age_group"] = df["age"].apply(age_group)
    return df

def load_to_bigquery(df: pd.DataFrame):
    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}"
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()
    print(f"✅ Loaded {job.output_rows} rows into {table_ref}")

def main():
    df_raw = extract_from_gcs()
    print("📥 Raw data:")
    print(df_raw)
    df_tx = transform(df_raw)
    print("🔄 Transformed:")
    print(df_tx)
    load_to_bigquery(df_tx)

if __name__ == "__main__":
    main()
