FROM openjdk:11-slim

RUN apt-get update && apt-get install -y \
    python3.10 python3.10-venv python3-pip python3.10-dev curl && \
    ln -s /usr/bin/python3.10 /usr/bin/python && \
    python -m pip install --upgrade pip

# Installer Spark
ENV SPARK_VERSION=3.5.1
RUN curl -L "https://archive.apache.org/dist/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop3.tgz" | tar -xz -C /opt/
ENV SPARK_HOME="/opt/spark-$SPARK_VERSION-bin-hadoop3"
ENV PATH="$SPARK_HOME/bin:$PATH"

# Installer pyspark + sparknlp
RUN pip install pyspark==$SPARK_VERSION sparknlp

WORKDIR /app
