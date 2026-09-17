FROM postgres:17

COPY init/ /docker-entrypoint-initdb.d/

ENV POSTGRES_USER=airflow
ENV POSTGRES_PASSWORD=airflow
ENV POSTGRES_DB=airflow

EXPOSE 5432