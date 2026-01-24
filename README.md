# Real-Time Social Media Sentiment Streaming (Kafka + Spark + InfluxDB + Grafana)

Une pipeline complète pour la gestion de message en streaming en temps réel. Le projet ingère des données texte de réseaux sociaux, analyse le sentiment des ces messages et fournit des visualisations des tendances globles dynamiquement via Grafana.

![Grafana Dashboard](lien_image_grafana.png)

## Features

* Streaming de données sociales en temps réel avec Kafka
* Analyse de sentiment automatisée via VADER
* Traitement distribué avec Spark Streaming
* Stockage des résultats dans InfluxDB (time-series database)
* Visualisation interactive et dashboards Grafana

## Installation

### Prérequis

Logiciels nécessaires (Windows & Linux) :

* Python ≥ 3.12
* Java ≥ 11
* Docker & Docker Compose (dernière version)
* Spark 4.0.1

### Dépendances Python

Le programme requiert les packages Python suivants :

- `confluent_kafka` (>= 2.0.0) : Kafka client pour la simulation de message en temps-réel
- `vaderSentiment` (>= 3.3.2) : Analyse de sentiment pour texte
- `influxdb-client` (>= 1.36.0) : Gestion deu stockage de données
- `pyspark` (>= 4.0.1) : Framework de traitement distribué pour gérer le real-time streaming

### Setup

Créer, activer un environnement virtuel :

```bash
python3 -m venv env
source env/bin/activate
```

```powershell
python -m venv env
env\Scripts\activate
```

Ensuite, installer les dépendances :

```bash
pip install -r requirements.txt
```

## Lancer l'infrastructure Docker

À la racine du projet, exécuter la commande ci-dessous pour initialiser l'infrastucture Docker :

```bash
docker compose up -d
```

Services démarrés :

| Service  | Port | Description                 |
| -------- | ---- | --------------------------- |
| Kafka    | 9092 | Broker Kafka                |
| InfluxDB | 8086 | Base de données Time-Series |
| Grafana  | 3000 | Dashboards                  |

## Lancer le Producer (hors Docker)

Exécuter la commande ci-dessous dans le dossier dans `/kafka` :

```bash
python producer.py
```

* Lit un CSV et envoie chaque ligne sur Kafka dans le topic `social_media_stream`.

## Lancer Spark Streaming (hors Docker)

Exécuter la commande ci-dessous dans le dossier `/spark` :

```bash
python3 main.py # Linux
python .\main.py # Windows
```

Rôle de Spark :
* Lit les messages Kafka
* Parse les JSON
* Analyse le sentiment avec VADER
* Écrit les résultats dans InfluxDB

Logs attendus :

```
Batch 10 written to InfluxDB
```

## Accéder à InfluxDB

→ [http://localhost:8086](http://localhost:8086)

* Username : `admin`
* Password : `admin123`

* Nom du Bucket par défaut : `sentiment_stream`

Menu → Data Explorer → Requête :

```flux
from(bucket: "sentiment_stream")
  |> range(start: -1h)
```

### Supprimer les anciennes données, si besoin (Retention Policy)

Dans InfluxDB :

* Settings → Buckets → `sentiment_stream` → Edit
* Choisir une durée : `1h`, `24h`, `7 jours`, `30 jours`

InfluxDB se charge d'expirer automatiquement les données.

## Créer le Dashboard Grafana

→ [http://localhost:3000](http://localhost:3000)

* Username : `admin`
* Password : `admin123`

* Ajouter InfluxDB comme data source

Paramètres :

* URL : `http://influxdb:8086`
* Token : `my-super-token`
* Org : `social_org`
* Bucket : `sentiment_stream`

### Exemple de requête Grafana (sentiment par entité)

```flux
from(bucket: "sentiment_stream")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "tweets")
  |> filter(fn: (r) => r._field == "predicted_sentiment")
  |> group(columns: ["entity", "_value"])
  |> count()
```


## License

Ce projet est sous licence MIT – une licence open source permissive qui permet l’utilisation, la modification et la distribution gratuites du logiciel.

Pour plus de détails, voir la documentation [MIT License](https://opensource.org/licenses/MIT).


## Auteurs

[@hacjoseph](https://github.com/hacjoseph)
[@imane-hashCode](https://github.com/imane-hashCode)
[@alipascal](https://github.com/alipascal)


Imane, Joseph, Alicia
