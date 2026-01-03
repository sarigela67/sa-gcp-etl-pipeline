GCP ETL Pipeline: Pulumi + GCS → BigQuery 🚀
End-to-end data engineering projects: \*\*Infrastructure as Code\*\* + \*\*Python ETL\*\* +\*\*SQL ETL\*\* In two different projects.


🎯 Project1 Overview(IaC):
 Depoyed IaC using pulumi →Created GCS Buckets → Bigquery Datasets

 Business Problem:Processed raw customer data (CSV) → analytics table (BigQuery) with derived insights.

🎯 Project2 Overview:
# GCP ETL Pipeline: NYC Taxi Analytics (Production-Ready) 🚀

[![Pulumi](https://img.shields.io/badge/Pulumi-IaC-yellow?logo=pulumi&logoColor=white)](https://pulumi.com)
[![BigQuery](https://img.shields.io/badge/SQL_ELT-MERGE-blue?logo=google-cloud&logoColor=white)](https://cloud.google.com/bigquery)
[![GCS](https://img.shields.io/badge/Data_Lake-Partitioned-orange?logo=google-cloud&logoColor=white)](https://cloud.google.com/storage)

**End-to-end GCP Data Engineering showcase**: Processes **4.1M NYC Yellow Taxi trips** (Jan 2024) using IaC + SQL ELT patterns.

## 🏗️ Architecture
Public NYC Parquet → GCS Raw → BQ Partitioned Load → SQL MERGE → Daily Analytics
d37ci6vzurychx.cloudfront.net/ → gs://sonic-earth-476701-m1-simple-de-raw/raw/ → etl_demo.raw_trips → etl_demo.daily_metrics

## 📊 Live Results
| Dataset | Rows | Partitioned | Schema |
|---------|------|-------------|--------|
| `etl_demo.raw_trips` | 4,104,534 | `tpep_pickup_datetime` (DAY) | 19 fields (autodetect) |
| `etl_demo.daily_metrics` | 31 days | - | `tip_rate_pct`, `avg_distance` |

**Demo Query**:
```sql
SELECT * FROM sonic-earth-476701-m1.etl_demo.daily_metrics 
ORDER BY trip_date DESC LIMIT 10;

**Production Features**:
    IaC: Pulumi YAML (GCS + BQ dataset) [Pulumi.yaml]

    Data Lake: GCS raw storage (sonic-earth-476701-m1-simple-de-raw)

    Partitioning: Daily partitions (cost/query optimization)

    ELT: SQL MERGE (upsert, incremental, idempotent)

    Schema: Parquet autodetect (VendorID→tip_amount)

**Quick start**:

# 1. Download NYC Taxi data (50MB)
curl -O https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet

# 2. Upload to GCS raw bucket
gsutil cp yellow_tripdata_2024-01.parquet gs://sonic-earth-476701-m1-simple-de-raw/raw/

# 3. Load partitioned table (autodetect)
bq load --replace --autodetect --source_format=PARQUET \
  --time_partitioning_type=DAY --time_partitioning_field=tpep_pickup_datetime \
  sonic-earth-476701-m1:etl_demo.raw_trips gs://sonic-earth-476701-m1-simple-de-raw/raw/yellow_tripdata_2024-01.parquet

# 4. Transform with MERGE
bq query --use_legacy_sql=false "
MERGE etl_demo.daily_metrics AS target
USING (SELECT DATE(tpep_pickup_datetime) trip_date, 
            AVG(tip_amount/NULLIF(total_amount,0))*100 tip_rate_pct, 
            AVG(trip_distance) avg_distance, COUNT(*) trip_count 
       FROM etl_demo.raw_trips GROUP BY 1) source 
ON target.trip_date=source.trip_date
WHEN MATCHED THEN UPDATE SET tip_rate_pct=source.tip_rate_pct, avg_distance=source.avg_distance, trip_count=target.trip_count+source.trip_count
WHEN NOT MATCHED THEN INSERT VALUES(source.trip_date,source.tip_rate_pct,source.avg_distance,source.trip_count)"

**[Metrics Demo](images/metrics.png)**:


