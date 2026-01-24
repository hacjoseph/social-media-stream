# Real-Time Social Media Sentiment Streaming (Kafka + Spark + InfluxDB + Grafana)

Une pipeline complète pour la gestion de message en streaming en temps réel. Le projet ingère des données texte de réseaux sociaux, analyse le sentiment des ces messages et fournit des visualisations des tendances globles dynamiquement via Grafana.

<p align="center">
  <img width="45%" alt="sentiment_pie_percentage" src="https://github.com/user-attachments/assets/37bb2a80-2694-436e-ae4a-ad0030d79cc7" />
  <img width="45%" alt="positive_ratio_bar_entities" src="https://github.com/user-attachments/assets/ccb8889a-6f08-4d3e-8bb1-83f55ddb4d5d" />
</p>

<p align="center">
  <img width="90%" alt="top10_entities_volume" src="https://github.com/user-attachments/assets/e70f9138-e8e2-41c8-9835-5dafb5062cb4" />
  <img width="90%" alt="sentiment_time_series_global" src="https://github.com/user-attachments/assets/78f07c72-9af9-416c-b476-49ab57cb1dd3" />
</p>


## Features

* Streaming de données sociales en temps réel avec Kafka
* Analyse de sentiment automatisée via VADER
* Traitement distribué avec Spark Streaming
* Stockage des résultats dans InfluxDB (time-series database)
* Visualisation interactive et dashboards Grafana

## How It Works / Architecture

Concrètement, la pipeline se décompose en plusieurs étapes :

1. **Producer (Kafka)**
   * Lit les données depuis un CSV ou flux social
   * Envoie chaque message dans le topic `social_media_stream` de Kafka

2. **Spark Streaming**
   * Consomme les messages Kafka en temps réel
   * Parse les JSON et calcule le sentiment avec **VADER**
   * Envoie les résultats dans **InfluxDB**

3. **InfluxDB**
   * Stocke les données temporelles des sentiments
   * Permet les requêtes et la gestion des données via Retention Policy

4. **Grafana**
   * Visualise les sentiments en dashboards interactifs
   * Permet le suivi par entité et la création de métriques personnalisées

**Architecture générale :**
<p align="center">
  <img width="50%" alt="architecture" src="https://github.com/user-attachments/assets/4ba428bd-9d5d-4e54-9567-88507deb31c1" />
</p>

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

Créer, et activer un environnement virtuel :

```bash
# linux
python3 -m venv env
source env/bin/activate

# windows
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

* Login : `admin`
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


## Auteurs

[@hacjoseph](https://github.com/hacjoseph)

[@imane-hashCode](https://github.com/imane-hashCode)

[@alipascal](https://github.com/alipascal)


## License

Ce projet est sous licence MIT – une licence open source permissive qui permet l’utilisation, la modification et la distribution gratuites du logiciel.

Pour plus de détails, voir la documentation [MIT License](https://opensource.org/licenses/MIT).
