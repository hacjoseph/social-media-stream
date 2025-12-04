import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages com.johnsnowlabs.nlp:spark-nlp_2.12:6.2.0, org.apache.spark:spark-streaming-kafka-0-10_2.12:3.3.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1 pyspark-shell'

import sparknlp
from pyspark.sql.functions import col, from_json
from pyspark.ml import Pipeline
from sparknlp.base import DocumentAssembler
from sparknlp.annotator import SentimentDLModel, UniversalSentenceEncoder
from pyspark.sql.types import StructType, StructField, StringType
from pyspark.sql import SparkSession


def main():
    spark = SparkSession.builder \
        .appName("KafkaSentimentAnalysis") \
        .getOrCreate()

    
    schema = StructType([
        StructField("tweet_id", StringType(), True),
        StructField("sentiment", StringType(), True),
        StructField("message", StringType(), True)
    ])
    
    dataFrame = spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "social_media_stream") \
        .load()
        
    data = dataFrame.selectExpr("CAST(value AS STRING) as json_str") \
        .select(from_json(col("json_str"), schema).alias("data")) \
        .select("data.*")
        
        
    
    # 1. Document Assembler
    documentAssembler = DocumentAssembler() \
        .setInputCol("message") \
        .setOutputCol("document")
        
    # 2. Universal Sentence Encoder (meilleur pour Twitter)
    use = UniversalSentenceEncoder.pretrained() \
        .setInputCols(["document"]) \
        .setOutputCol("sentence_embeddings")
        
    # 3. Modèle de sentiment Twitter
    sentimentDetector = SentimentDLModel.pretrained("sentimentdl_use_twitter") \
        .setInputCols(["sentence_embeddings"]) \
        .setOutputCol("sentiment") \
        .setThreshold(0.6)  # Seuil de confiance
    
    # 4. Pipeline
    pipeline = Pipeline(stages=[
        documentAssembler,
        use,
        sentimentDetector
    ])
    
    # 5. Entraîner le modèle
    result = pipeline.fit(spark.createDataFrame([[""]], ["message"])).transform(data)
    
    # Afficher les résultats
    query = result.select(
        "tweet_id",
        "sentiment",
        "sentiment.resul"
    ).writeStream\
    .format("console")\
    .outputMode("append")\
    .start()
    
    query.awaitTermination()
    
    
if __name__ == "__main__":
    main() 