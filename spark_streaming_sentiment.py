import sys

from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType, TimestampType

import spacy

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


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

    df = spark.readStream.option("sep",",").schema(myschema).csv("data")
    
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


    