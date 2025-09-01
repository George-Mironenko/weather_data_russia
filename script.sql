CREATE TABLE IF NOT EXISTS cities (
            city_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            country INT,
            lat DECIMAL(9,6) NOT NULL,
            lon DECIMAL(9,6) NOT NULL,
);

CREATE TABLE IF NOT EXISTS weather_conditions (
            condition_id INT PRIMARY KEY,
            main VARCHAR(50) NOT NULL,
            description TEXT NOT NULL,
            icon VARCHAR(10) NOT NULL
);

CREATE TABLE IF NOT EXISTS weather_observations (
            weather_observations_id SERIAL PRIMARY KEY
            city_id BIGINT REFERENCES cities(city_id),
            condition_id INT REFERENCES weather_conditions(condition_id),
            temp DECIMAL(6,2) NOT NULL,
            temp_min DECIMAL(6,2) NOT NULL,
            temp_max DECIMAL(6,2) NOT NULL,
            pressure INT NOT NULL,
            humidity INT NOT NULL,
            visibility INT NOT NULL,
            wind_speed DECIMAL(5,2) NOT NULL,
            wind_deg INT NOT NULL,
            clouds_all INT NOT NULL,
            recorded_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
            sunrise TIMESTAMP WITHOUT TIME ZONE,
            sunset TIMESTAMP WITHOUT TIME ZONE,
            created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS "Country" (
    "id" SERIAL PRIMARY KEY,
    "name" VARCHAR(40) NOT NULL
);

ALTER table "cities"
    add CONSTRAINT "cities_country_foreign" foreign key("country") REFERENCES "County"("id");