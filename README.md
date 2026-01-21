GCP ETL Pipelines: Pulumi + GCS + BigQuery
End-to-end data engineering projects showcasing Infrastructure as Code + Python/SQL ETL on Google Cloud Platform.

Project 1 – IaC + Simple CSV ETL :

Deployed GCP resources using Pulumi IaC: GCS buckets + BigQuery datasets/tables

Processed raw customer CSV data → analytics table with derived insights (aggregations, metrics)




Project 2 – NYC Taxi Analytics (Production-Ready):

**End-to-end GCP Data Engineering showcase**: Processes **4.1M NYC Yellow Taxi trips** (Jan 2024) using IaC + SQL ELT patterns.

🏗️ Architecture :

Public NYC Parquet → GCS Raw → BigQuery Partitioned → SQL MERGE → Daily Metrics
[NYC Dataset](https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet)
           ↓
gs://sonic-earth-476701-m1-simple-de-raw/raw/
           ↓  
etl_demo.raw_trips (DAY partitioned on tpep_pickup_datetime)
           ↓
etl_demo.daily_metrics (tip_rate_pct, avg_distance)

📊 Live Results :

| Dataset                | Rows      | Partitioning               | Key Fields                 |
| ---------------------- | --------- | -------------------------- | -------------------------- |
| etl_demo.raw_trips     | 4,104,534 | DAY (tpep_pickup_datetime) | 19 fields (autodetect)     |
| etl_demo.daily_metrics | 31 days   | -                          | tip_rate_pct, avg_distance |

Demo Query:

SELECT * FROM `sonic-earth-476701-m1.etl_demo.daily_metrics` 
ORDER BY trip_date DESC 
LIMIT 10;

Production Features :

IaC: Pulumi YAML provisioning GCS + BigQuery dataset [Pulumi.yaml]
Data Lake: GCS raw storage (sonic-earth-476701-m1-simple-de-raw)
Partitioning: Daily partitions for cost/query optimization
ELT: SQL MERGE (upsert, incremental, idempotent)
Schema: Parquet autodetect (VendorID→tip_amount)


# 1. Download NYC Taxi data (50MB):
curl -O https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet

# 2. Upload to GCS raw bucket:
gsutil cp yellow_tripdata_2024-01.parquet gs://sonic-earth-476701-m1-simple-de-raw/raw/

# 3. Load partitioned table:
bq load --replace --autodetect --source_format=PARQUET \
  --time_partitioning_type=DAY --time_partitioning_field=tpep_pickup_datetime \
  sonic-earth-476701-m1:etl_demo.raw_trips gs://sonic-earth-476701-m1-simple-de-raw/raw/yellow_tripdata_2024-01.parquet

# 4. Transform with MERGE:
" MERGE etl_demo.daily_metrics AS target
USING (SELECT DATE(tpep_pickup_datetime) trip_date, 
            AVG(tip_amount/NULLIF(total_amount,0))*100 tip_rate_pct, 
            AVG(trip_distance) avg_distance, COUNT(*) trip_count 
       FROM etl_demo.raw_trips GROUP BY 1) source 
ON target.trip_date=source.trip_date
WHEN MATCHED THEN UPDATE SET tip_rate_pct=source.tip_rate_pct, avg_distance=source.avg_distance, trip_count=target.trip_count+source.trip_count
WHEN NOT MATCHED THEN INSERT VALUES(source.trip_date,source.tip_rate_pct,source.avg_distance,source.trip_count)"



