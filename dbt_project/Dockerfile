FROM python:3.12-slim

RUN pip install --no-cache-dir dbt-postgres==1.9.0

WORKDIR /dbt

COPY dbt_project.yml .
COPY profiles.yml .
COPY models/ ./models/

# По умолчанию — просто показать версию.
# Реальная команда (dbt run) задаётся в docker-compose.
CMD ["dbt", "--version"]