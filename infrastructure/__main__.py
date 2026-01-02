import pulumi
import pulumi_gcp as gcp

# Use Pulumi config for project/region
config = pulumi.Config("gcp")
project = config.require("project")
region = config.get("region") or "us-central1"

bucket = gcp.storage.Bucket(
    "raw-data-bucket",
    name=f"{project}-simple-de-raw",
    location="US",
    uniform_bucket_level_access=True,
    force_destroy=True,
)

dataset = gcp.bigquery.Dataset(
    "demo-dataset",
    dataset_id="simple_de_demo",
    friendly_name="Simple DE Demo",
    description="Beginner demo for GCS → BigQuery",
    location="US",
)

table = gcp.bigquery.Table(
    "demo-table",
    dataset_id=dataset.dataset_id,
    table_id="people",
    deletion_protection=False,
    schema="""[
      {"name": "id", "type": "INT64", "mode": "REQUIRED"},
      {"name": "name", "type": "STRING", "mode": "NULLABLE"},
      {"name": "age", "type": "INT64", "mode": "NULLABLE"},
      {"name": "age_group", "type": "STRING", "mode": "NULLABLE"}
    ]""",
)

pulumi.export("bucket_name", bucket.name)
pulumi.export("dataset_id", dataset.dataset_id)
pulumi.export("table_id", table.table_id)

