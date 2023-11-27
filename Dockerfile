FROM apache/airflow:2.3.2
USER root
RUN apt-get update \
    && apt-get -y --no-install-recommends install  \
        openjdk-11-jre-headless \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
USER airflow
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
RUN pip install --upgrade pip
RUN pip install --no-cache-dir "apache-airflow==2.3.2"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip uninstall -y argparse attr
