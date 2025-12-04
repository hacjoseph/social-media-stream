import sys

from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType, TimestampType

import os
# scala version 2.13.16
# spark version 4.0.1
version = "2.13:4.0.1"
os.environ['PYSPARK_SUBMIT_ARGS'] = f'--packages org.apache.spark:spark-streaming-kafka-0-10_{version},org.apache.spark:spark-sql-kafka-0-10_{version} pyspark-shell'


import spacy

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# VARIABLES ---------------------------------------------------------
topic = 'social_media_stream'
host = "localhost:9092"


# METHODS -----------------------------------------------------------

def sentimentAnalysis(sentence):
    if sentence is None:
        return "None"
    
    analyzer = SentimentIntensityAnalyzer()
    
    vs = analyzer.polarity_scores(sentence)
    vs.pop('compound')

    result = max(vs, key=vs.get)
    analyzer = SentimentIntensityAnalyzer()
    
    if result == 'neg':
        return "Negative"
    if result == 'neu':
        return "Neutre"
    if result == 'pos':
        return "Positive"


nlp = spacy.load("fr_core_news_lg")
def keywordsDetection(sentence):
    if sentence is None:
        return "None"
    doc = nlp(sentence)
    keywords = [chunk.text for chunk in doc.noun_chunks]
    return keywords


# MAIN -----------------------------------------------------------

if __name__ == "__main__":

    spark = SparkSession\
        .builder\
        .appName("MessageSentimentAnalysis")\
        .getOrCreate()
    
    myschema = StructType(
        [StructField('timestamp', TimestampType(), True),
        StructField('user', StringType(), True), 
        StructField('text', StringType(), True)]
    )

    # df = spark.readStream.option("sep",",").schema(myschema).csv("data")
    df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", host) \
    .option("subscribe", topic) \
    .load()

    df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
    print(df)
    
    cols = ['timestamp', 'user', 'text']
    socialMediaPosts = df.select(*cols)

    socialMediaPosts = socialMediaPosts.withColumn("sentiment", sentimentAnalysis(socialMediaPosts["text"]))
    socialMediaPosts = socialMediaPosts.withColumn("keywords", keywordsDetection(socialMediaPosts["text"]))


    #sentiment analysis of socialMediaPosts
    # pur les groupBy 'complete' 
    query = socialMediaPosts\
        .writeStream\
        .outputMode('append')\
        .format('console')\
        .trigger(processingTime="2 seconds")\
        .start()

    query.awaitTermination()


    