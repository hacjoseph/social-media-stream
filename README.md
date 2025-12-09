
# Real-Time Social Media Sentiment Streaming (Kafka + Spark + InfluxDB + Grafana)
## Aperçu du projet

Ce projet met en place une pipeline de streaming complète :

Producer (Python) ➜ envoie des tweets dans Kafka

Spark Structured Streaming ➜ consomme Kafka, applique VADER et écrit dans InfluxDB

InfluxDB ➜ stocke les données

Grafana ➜ visualisation temps réel (dashboard par entité / sentiment)

Kafka, InfluxDB et Grafana tournent dans Docker.
Le Producer et Spark tournent localement (Windows ou Linux).

## 1. Prérequis
Logiciels requis (Windows & Linux)
    Python	≥ 3.12
    Java	≥ 11
    Docker & Docker Compose	Dernière version
    Spark	4.0.1
pip	Dernière version

## 2. Installation des dépendances Python

Dans la racine du projet :
Créer un environnement virtuel et installer les dépendances
    - python -m venv env

    Linux :
        - env\Scripts\activate
    Windows :
        - source env/bin/activate

    - pip install -r requirements.txt


Dépendances principales :

confluent_kafka

vaderSentiment

influxdb-client

pyspark

## 3. Lancer l’infrastructure Docker (Kafka + InfluxDB + Grafana)

À la racine du projet :

    docker compose up -d


Cela démarre automatiquement :

Service	Port	Description
Kafka	9092	Broker Kafka
InfluxDB	8086	Base de données Time-Series
Grafana	3000	Dashboards

## 4. Lancer le Producer (hors Docker)

Dans /kafka :

    - python producer.py


Le producer lit un CSV et envoie chaque ligne sur Kafka dans le topic : social_media_stream

## 5. Lancer Spark Streaming (hors Docker)

Dans /spark:

Linux :
python3 main.py

Windows :
python .\main.py


Spark :

lit Kafka

parse les JSON

calcule le sentiment via VADER

envoie les résultats dans InfluxDB

Tu verras des logs du type :

 - Batch 10 written to InfluxDB


Cela signifie que les données ont bien été envoyées.

## 6. Accéder à InfluxDB

➡️ http://localhost:8086

Login :

Username : admin

Password : admin123

Bucket par défaut :

sentiment_stream

Vérifier les données :

Menu → Data Explorer
Puis requête :

    from(bucket: "sentiment_stream")
        |> range(start: -1h)

## 7. Créer le Dashboard Grafana

➡️ http://localhost:3000


LOGIN : admin / admin123

Ajouter InfluxDB comme data source

Connections ➜ Add data source

Choisir InfluxDB

Paramètres :

URL : http://influxdb:8086

Token : my-super-token

Org : social_org

Bucket : sentiment_stream

## 8. Exemple de requête Grafana (sentiment par entité)
from(bucket: "sentiment_stream")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "tweets")
  |> filter(fn: (r) => r._field == "predicted_sentiment")
  |> group(columns: ["entity", "_value"])
  |> count()

## 9. Supprimer les anciennes données (Retention Policy)

Dans InfluxDB :

Settings → Buckets → sentiment_stream → Edit
Choisis une durée :

1h

24h

7 jours

30 jours

InfluxDB s'occupe d’expirer les données automatiquement.