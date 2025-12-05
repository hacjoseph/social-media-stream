FROM bitnami/spark:3.3.1

USER root

# Installer Python + dépendances système
RUN install_packages python3 python3-pip openjdk-17-jdk wget curl

# Mettre à jour pip
RUN pip3 install --upgrade pip

# Installer les dépendances Python avec versions compatibles
RUN pip3 install --no-cache-dir \
    pyspark==3.5.0 \
    spark-nlp==5.5.1 \
    vaderSentiment==3.3.2 \
    confluent-kafka==2.3.0

# Créer le répertoire pour les JARs si nécessaire
RUN mkdir -p /opt/bitnami/spark/jars

# Télécharger le driver JDBC MySQL
RUN wget -q https://repo1.maven.org/maven2/mysql/mysql-connector-j/8.0.33/mysql-connector-j-8.0.33.jar \
    -P /opt/bitnami/spark/jars/

# Télécharger Spark NLP JAR (si besoin pour Spark Submit)
RUN wget -q https://repo1.maven.org/maven2/com/johnsnowlabs/nlp/spark-nlp_2.12/5.5.1/spark-nlp_2.12-5.5.1.jar \
    -P /opt/bitnami/spark/jars/

# Définir les variables d'environnement
ENV SPARK_HOME=/opt/bitnami/spark
ENV PATH=$PATH:$SPARK_HOME/bin
ENV PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9.7-src.zip:$PYTHONPATH

# Retourner à l'utilisateur non-root
USER 1001

WORKDIR /app

# Point d'entrée par défaut
CMD ["python3"]
