import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.13:4.0.1,org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.1 pyspark-shell'

from pyspark.sql.functions import col, from_json, udf
from pyspark.sql.types import StructType, StructField, StringType
from pyspark.sql import SparkSession
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from influxdb_client import InfluxDBClient, Point, WritePrecision
import time


INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "my-super-token"
INFLUX_ORG = "social_org"
INFLUX_BUCKET = "sentiment_stream"

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api()


def write_to_influxdb(batch_df, batch_id):
    """
    Fonction exécutée à chaque micro-batch Spark.
    """
    rows = batch_df.collect()

    if not rows:
        return

    for row in rows:
        point = (
            Point("tweets")
            .tag("entity", row.entity)  
            .tag("predicted_sentiment", row.predicted_sentiment)
            .field("tweet_id", row.tweet_id)
            .field("message", row.message)
            .field("sentiment_original", row.sentiment if row.sentiment else "unknown")
            .time(int(time.time_ns()), WritePrecision.NS)
        )

        write_api.write(
            bucket=INFLUX_BUCKET,
            org=INFLUX_ORG,
            record=point
        )

    print(f"✔ Batch {batch_id} written to InfluxDB")

def main():
    spark = SparkSession.builder \
        .appName("KafkaSentimentAnalysis") \
        .getOrCreate()

    kafka_bootstrap_servers = "localhost:9092"
    kafka_topic = "social_media_stream"
    
    analyzer = SentimentIntensityAnalyzer()
    
    def vader_sentiment_udf(text):
        if text is None or text.strip() == "":
            return "neutral"
        score = analyzer.polarity_scores(text)["compound"]
        if score >= 0.05:
            return "positive"
        elif score <= -0.05:
            return "negative"
        else:
            return "neutral"
        
    vader_udf = udf(vader_sentiment_udf, StringType())
    schema = StructType([
        StructField("tweet_id", StringType(), True),
        StructField("entity", StringType(), True),
        StructField("sentiment", StringType(), True),
        StructField("message", StringType(), True)
    ])
    
    
    
    dataFrame = spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("subscribe", kafka_topic) \
        .load()
        
    data = dataFrame.selectExpr("CAST(value AS STRING) as json_str") \
        .select(from_json(col("json_str"), schema).alias("data")) \
        .select("data.*")
        
    result = data.withColumn("predicted_sentiment", vader_udf(col("message")))
    
        
    query = result.writeStream\
        .foreachBatch(write_to_influxdb) \
        .outputMode("append")\
        .option("checkpointLocation", "/tmp/checkpoints/sentiment") \
        .start()
    
    query.awaitTermination()
    
    
if __name__ == "__main__":
    main() 