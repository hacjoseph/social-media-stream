import os
# os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.13:4.0.1,org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.1 pyspark-shell'
version = "2.13:4.0.1"
os.environ['PYSPARK_SUBMIT_ARGS'] = f'--packages org.apache.spark:spark-streaming-kafka-0-10_{version},org.apache.spark:spark-sql-kafka-0-10_{version} pyspark-shell'


from pyspark.sql.functions import col, from_json, udf, current_timestamp, date_format
from pyspark.ml import Pipeline
from pyspark.sql.types import StructType, StructField, StringType
from pyspark.sql import SparkSession
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from datetime import datetime


def main():
    spark = SparkSession.builder \
        .appName("KafkaSentimentAnalysis") \
        .getOrCreate()

    kafka_bootstrap_servers = "localhost:9092"
    kafka_topic = "social_media_stream"
    
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
        StructField("sentiment", StringType(), True),
        StructField("message", StringType(), True)
    ])
    
    
    analyzer = SentimentIntensityAnalyzer()
    
    dataFrame = spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "social_media_stream") \
        .load()
        
    data = dataFrame.selectExpr("CAST(value AS STRING) as json_str") \
        .select(from_json(col("json_str"), schema).alias("data")) \
        .select("data.*")
        
    resultData = data.withColumn("predicted_sentiment", vader_udf(col("message")))
    resultData = resultData.withColumn("timestamp", current_timestamp())
    resultData = resultData.withColumn("date", date_format(current_timestamp(), "yyyy-MM-dd"))
        
    # Afficher les résultats
    query = resultData.select(
        "tweet_id",
        "sentiment",
        "message",
        "predicted_sentiment",
        "timestamp",
        "date",
    ).writeStream\
    .format("console")\
    .outputMode("append")\
    .start()
    
    query.awaitTermination()
    
    
if __name__ == "__main__":
    main() 