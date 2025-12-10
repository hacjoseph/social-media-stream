import csv
import time
import json
from confluent_kafka import Producer

conf = {
    'bootstrap.servers': 'localhost:9092'
}

producer = Producer(conf)

dataset = '../dataset/twitter_dataset.csv'
topic = 'social_media_stream'

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')
        
        
with open(dataset, 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    
    for row in reader:
        
        if len(row) < 5:
            continue
        
        # colonne --> timestamps,tweet_id,entity,sentiment,message
        colonne = {
            "timestamp": row[0],
            "tweet_id": row[1],
            "entity": row[2],
            "sentiment": row[3],
            "message": row[4],
        }
        
        message = json.dumps(colonne)
        print(f"Sending message: {message}")
        producer.produce(topic, value=message, callback=delivery_report)
        producer.poll(0)
        time.sleep(1)

producer.flush()
