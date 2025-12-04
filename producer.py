import csv
import time
import json
from confluent_kafka import Producer
from transformers import pipeline

# Configuration Kafka
conf = {
    "bootstrap.servers": "localhost:9092"
}

producer = Producer(conf)

dataset_path = "dataset/twitter_dataset.csv"
topic = "social_media_stream"

# Chargement du modèle HuggingFace pour classification sentiment
sentiment_classifier = pipeline(
    task="text-classification",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    tokenizer="cardiffnlp/twitter-roberta-base-sentiment-latest"
)

def predict_sentiment(text: str):
    if not text or text.strip() == "":
        return "neutral", 0.0
    result = sentiment_classifier(text, truncation=True)[0]
    label = result["label"].lower()  # ex: POSITIVE -> positive
    score = float(result["score"])
    return label, score

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def main():
    with open(dataset_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)

        # Sauter l'en-tête si présent
        header = next(reader, None)
        if header and ("tweet_id" in header[0].lower() or "id" in header[0].lower()):
            print(f"Header detected: {header}")

        for row in reader:
            if len(row) < 4:
                continue

            tweet_id = row[0]
            entity = row[1]
            original_sentiment = row[2]
            message_text = row[3]

            predicted_sentiment, score = predict_sentiment(message_text)

            data = {
                "tweet_id": tweet_id,
                "entity": entity,
                "original_sentiment": original_sentiment,
                "sentiment": predicted_sentiment,
                "sentiment_score": score,
                "message": message_text,
            }

            message = json.dumps(data, ensure_ascii=False)
            print(f"Sending message: {message}")
            producer.produce(topic, value=message.encode("utf-8"), callback=delivery_report)
            producer.poll(0)
            time.sleep(1)  # petit délai pour ne pas saturer Kafka

    producer.flush()

if __name__ == "__main__":
    main()
