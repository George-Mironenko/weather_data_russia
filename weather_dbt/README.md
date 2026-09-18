# weather_dbt

dbt project that replaces the hand-written `all_data` Postgres VIEW
(previously defined in `sql_scripts/script_create.sql`) with a tested dbt model.

## Layout

```
weather_dbt/
├── dbt_project.yml
├── profiles.yml.example
├── models/
│   ├── staging/
│   │   ├── sources.yml              # declares the raw tables
│   │   ├── schema.yml               # tests on staging models
│   │   ├── stg_cities.sql
│   │   ├── stg_country.sql
│   │   ├── stg_weather_main_types.sql
│   │   ├── stg_weather_icons.sql
│   │   ├── stg_weather_conditions.sql
│   │   └── stg_weather_observations.sql
│   └── marts/
│       ├── all_data.sql             # rebuilds the old `all_data` view
│       └── schema.yml               # tests on all_data
```

## Setup

1. Copy this `weather_dbt/` folder into the root of the `weather_data_russia` repo,
   alongside `docker-compose.yml`.

2. Install dbt (in a virtualenv is easiest):

   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install dbt-postgres
   ```

3. Bring up the stack so Postgres is reachable:

   ```bash
   docker-compose up -d postgres
   ```

4. Set up your profile. Either copy `profiles.yml.example` to `~/.dbt/profiles.yml`,
   or point dbt at this folder:

   ```bash
   export DBT_PROFILES_DIR=$(pwd)/weather_dbt
   cp weather_dbt/profiles.yml.example weather_dbt/profiles.yml
   ```

   Use `host: localhost` if running dbt from your machine (docker-compose
   publishes port 5432), or `host: postgres` if running dbt from inside the
   same Docker network.

5. Make sure the raw tables already exist (they're created by
   `sql_scripts/script_create.sql`, typically run once against the `airflow`
   Postgres database) and that `weather_observations` has at least one row
   -- otherwise the `not_null` tests on `all_data` will have nothing to check
   but the joins will still validate structurally.

## Running it

```bash
cd weather_dbt
dbt debug     # sanity-check the connection
dbt build     # runs every model AND every test
```

Or split it up:

```bash
dbt run       # materializes stg_* views and all_data
dbt test      # runs not_null / unique / relationships tests
```

## What changed vs. the old setup

- `sql_scripts/script_create.sql`: the `CREATE OR REPLACE VIEW all_data ...`
  block has been removed (see `patched_sql_scripts/script_create.sql` in this
  delivery) since dbt now owns that object.
- `dags/load_to_cloud.py` needs no changes -- it still just does
  `SELECT * FROM all_data`, and dbt's `all_data` view has the same name,
  schema, and columns as before.

## Suggested next step

Add a CI job (next to `.github/workflows/build-airflow.yml`) that spins up
Postgres and runs `dbt build` on every PR, so the view and its tests are
checked automatically before merge.
