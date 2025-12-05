import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.13:4.0.1,org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.1 pyspark-shell'

from pyspark.sql.functions import col, from_json, udf
from pyspark.sql.types import StructType, StructField, StringType
from pyspark.sql import SparkSession
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# def write_to_mysql(batch_df, batch_id):
#     (
#         batch_df.write
#         .format("jdbc")
#         .option("url", "jdbc:mysql://localhost:3306/social_stream")
#         .option("dbtable", "tweets_sentiment")
#         .option("user", "root")
#         .option("password", "password")
#         .option("driver", "com.mysql.cj.jdbc.Driver")
#         .mode("append")
#         .save()
#     )


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
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("subscribe", kafka_topic) \
        .load()
        
    data = dataFrame.selectExpr("CAST(value AS STRING) as json_str") \
        .select(from_json(col("json_str"), schema).alias("data")) \
        .select("data.*")
        
    result = data.withColumn("predicted_sentiment", vader_udf(col("message")))
        
    # Afficher les résultats
    query = result.select(
        "tweet_id",
        "message",
        "predicted_sentiment"
    ).writeStream\
    .format("console")\
    .outputMode("append")\
    .start()
    
    query.awaitTermination()
    
    
if __name__ == "__main__":
    main() 