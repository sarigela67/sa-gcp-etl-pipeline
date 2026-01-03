MERGE etl_demo.daily_metrics AS target
USING (
  SELECT
    DATE(tpep_pickup_datetime) AS trip_date,
    AVG(tip_amount / NULLIF(total_amount, 0)) * 100 AS tip_rate_pct,
    AVG(trip_distance) AS avg_distance,
    COUNT(*) AS trip_count
  FROM `sonic-earth-476701-m1.etl_demo.raw_trips`
  GROUP BY trip_date
) AS source
ON target.trip_date = source.trip_date
WHEN MATCHED THEN
  UPDATE SET
    tip_rate_pct = source.tip_rate_pct,
    avg_distance = source.avg_distance,
    trip_count = source.trip_count + target.trip_count
WHEN NOT MATCHED THEN
  INSERT (trip_date, tip_rate_pct, avg_distance, trip_count)
  VALUES (source.trip_date, source.tip_rate_pct, source.avg_distance, source.trip_count);

--check
SELECT * FROM etl_demo.daily_metrics ORDER BY trip_date DESC LIMIT 10# NYC Taxi SQL MERGE 
