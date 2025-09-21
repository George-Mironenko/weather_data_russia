CREATE TABLE IF NOT EXISTS cities (
            city_id SERIAL PRIMARY KEY,
            name VARCHAR(100) unique NOT NULL,
            country INT,
            lat DECIMAL(9,6) NOT NULL,
            lon DECIMAL(9,6) NOT NULL
);

CREATE TABLE IF NOT EXISTS weather_main_types (
    main_id SERIAL PRIMARY KEY,
    main_name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS weather_icons (
    icons_id SERIAL PRIMARY KEY,
    icon_code VARCHAR(3)
);

CREATE TABLE IF NOT EXISTS weather_conditions (
            condition_id INT PRIMARY KEY,
            main INT  REFERENCES weather_main_types(main_id),
            description TEXT NOT NULL,
            icon INT    REFERENCES weather_icons(icons_id)
);

CREATE TABLE IF NOT EXISTS weather_observations (
            weather_observations_id SERIAL PRIMARY KEY,
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

CREATE TABLE IF NOT EXISTS country (
    "id" SERIAL PRIMARY KEY,
    "name" VARCHAR(40) NOT NULL
);

ALTER table "cities"
    add CONSTRAINT "cities_country_foreign" foreign key("country") REFERENCES "country"("id");

INSERT INTO weather_main_types (main_name) VALUES
('Thunderstorm'),
('Drizzle'),
('Rain'),
('Snow'),
('Mist'),
('Smoke'),
('Haze'),
('Dust'),
('Fog'),
('Sand'),
('Ash'),
('Squall'),
('Tornado'),
('Clear'),
('Clouds');

INSERT INTO weather_icons (icon_code) VALUES
('01d'), ('01n'),
('02d'), ('02n'),
('03d'), ('03n'),
('04d'), ('04n'),
('09d'), ('09n'),
('10d'), ('10n'),
('11d'), ('11n'),
('13d'), ('13n'),
('50d'), ('50n');


INSERT INTO weather_conditions (condition_id, main, description, icon) VALUES
-- Thunderstorm
(200, (SELECT main_id FROM weather_main_types WHERE main_name = 'Thunderstorm'), 'thunderstorm with light rain', (SELECT icons_id FROM weather_icons WHERE icon_code = '11d')),
(201, (SELECT main_id FROM weather_main_types WHERE main_name = 'Thunderstorm'), 'thunderstorm with rain', (SELECT icons_id FROM weather_icons WHERE icon_code = '11d')),
(202, (SELECT main_id FROM weather_main_types WHERE main_name = 'Thunderstorm'), 'thunderstorm with heavy rain', (SELECT icons_id FROM weather_icons WHERE icon_code = '11d')),
(210, (SELECT main_id FROM weather_main_types WHERE main_name = 'Thunderstorm'), 'light thunderstorm', (SELECT icons_id FROM weather_icons WHERE icon_code = '11d')),
(211, (SELECT main_id FROM weather_main_types WHERE main_name = 'Thunderstorm'), 'thunderstorm', (SELECT icons_id FROM weather_icons WHERE icon_code = '11d')),
(212, (SELECT main_id FROM weather_main_types WHERE main_name = 'Thunderstorm'), 'heavy thunderstorm', (SELECT icons_id FROM weather_icons WHERE icon_code = '11d')),
(221, (SELECT main_id FROM weather_main_types WHERE main_name = 'Thunderstorm'), 'ragged thunderstorm', (SELECT icons_id FROM weather_icons WHERE icon_code = '11d')),
(230, (SELECT main_id FROM weather_main_types WHERE main_name = 'Thunderstorm'), 'thunderstorm with light drizzle', (SELECT icons_id FROM weather_icons WHERE icon_code = '11d')),
(231, (SELECT main_id FROM weather_main_types WHERE main_name = 'Thunderstorm'), 'thunderstorm with drizzle', (SELECT icons_id FROM weather_icons WHERE icon_code = '11d')),
(232, (SELECT main_id FROM weather_main_types WHERE main_name = 'Thunderstorm'), 'thunderstorm with heavy drizzle', (SELECT icons_id FROM weather_icons WHERE icon_code = '11d')),

-- Drizzle
(300, (SELECT main_id FROM weather_main_types WHERE main_name = 'Drizzle'), 'light intensity drizzle', (SELECT icons_id FROM weather_icons WHERE icon_code = '09d')),
(301, (SELECT main_id FROM weather_main_types WHERE main_name = 'Drizzle'), 'drizzle', (SELECT icons_id FROM weather_icons WHERE icon_code = '09d')),
(302, (SELECT main_id FROM weather_main_types WHERE main_name = 'Drizzle'), 'heavy intensity drizzle', (SELECT icons_id FROM weather_icons WHERE icon_code = '09d')),
(310, (SELECT main_id FROM weather_main_types WHERE main_name = 'Drizzle'), 'light intensity drizzle rain', (SELECT icons_id FROM weather_icons WHERE icon_code = '09d')),
(311, (SELECT main_id FROM weather_main_types WHERE main_name = 'Drizzle'), 'drizzle rain', (SELECT icons_id FROM weather_icons WHERE icon_code = '09d')),
(312, (SELECT main_id FROM weather_main_types WHERE main_name = 'Drizzle'), 'heavy intensity drizzle rain', (SELECT icons_id FROM weather_icons WHERE icon_code = '09d')),
(313, (SELECT main_id FROM weather_main_types WHERE main_name = 'Drizzle'), 'shower rain and drizzle', (SELECT icons_id FROM weather_icons WHERE icon_code = '09d')),
(314, (SELECT main_id FROM weather_main_types WHERE main_name = 'Drizzle'), 'heavy shower rain and drizzle', (SELECT icons_id FROM weather_icons WHERE icon_code = '09d')),
(321, (SELECT main_id FROM weather_main_types WHERE main_name = 'Drizzle'), 'shower drizzle', (SELECT icons_id FROM weather_icons WHERE icon_code = '09d')),

-- Rain
(500, (SELECT main_id FROM weather_main_types WHERE main_name = 'Rain'), 'light rain', (SELECT icons_id FROM weather_icons WHERE icon_code = '10d')),
(501, (SELECT main_id FROM weather_main_types WHERE main_name = 'Rain'), 'moderate rain', (SELECT icons_id FROM weather_icons WHERE icon_code = '10d')),
(502, (SELECT main_id FROM weather_main_types WHERE main_name = 'Rain'), 'heavy intensity rain', (SELECT icons_id FROM weather_icons WHERE icon_code = '10d')),
(503, (SELECT main_id FROM weather_main_types WHERE main_name = 'Rain'), 'very heavy rain', (SELECT icons_id FROM weather_icons WHERE icon_code = '10d')),
(504, (SELECT main_id FROM weather_main_types WHERE main_name = 'Rain'), 'extreme rain', (SELECT icons_id FROM weather_icons WHERE icon_code = '10d')),
(511, (SELECT main_id FROM weather_main_types WHERE main_name = 'Rain'), 'freezing rain', (SELECT icons_id FROM weather_icons WHERE icon_code = '13d')),
(520, (SELECT main_id FROM weather_main_types WHERE main_name = 'Rain'), 'light intensity shower rain', (SELECT icons_id FROM weather_icons WHERE icon_code = '09d')),
(521, (SELECT main_id FROM weather_main_types WHERE main_name = 'Rain'), 'shower rain', (SELECT icons_id FROM weather_icons WHERE icon_code = '09d')),
(522, (SELECT main_id FROM weather_main_types WHERE main_name = 'Rain'), 'heavy intensity shower rain', (SELECT icons_id FROM weather_icons WHERE icon_code = '09d')),
(531, (SELECT main_id FROM weather_main_types WHERE main_name = 'Rain'), 'ragged shower rain', (SELECT icons_id FROM weather_icons WHERE icon_code = '09d')),

-- Snow
(600, (SELECT main_id FROM weather_main_types WHERE main_name = 'Snow'), 'light snow', (SELECT icons_id FROM weather_icons WHERE icon_code = '13d')),
(601, (SELECT main_id FROM weather_main_types WHERE main_name = 'Snow'), 'snow', (SELECT icons_id FROM weather_icons WHERE icon_code = '13d')),
(602, (SELECT main_id FROM weather_main_types WHERE main_name = 'Snow'), 'heavy snow', (SELECT icons_id FROM weather_icons WHERE icon_code = '13d')),
(611, (SELECT main_id FROM weather_main_types WHERE main_name = 'Snow'), 'sleet', (SELECT icons_id FROM weather_icons WHERE icon_code = '13d')),
(612, (SELECT main_id FROM weather_main_types WHERE main_name = 'Snow'), 'light shower sleet', (SELECT icons_id FROM weather_icons WHERE icon_code = '13d')),
(613, (SELECT main_id FROM weather_main_types WHERE main_name = 'Snow'), 'shower sleet', (SELECT icons_id FROM weather_icons WHERE icon_code = '13d')),
(615, (SELECT main_id FROM weather_main_types WHERE main_name = 'Snow'), 'light rain and snow', (SELECT icons_id FROM weather_icons WHERE icon_code = '13d')),
(616, (SELECT main_id FROM weather_main_types WHERE main_name = 'Snow'), 'rain and snow', (SELECT icons_id FROM weather_icons WHERE icon_code = '13d')),
(620, (SELECT main_id FROM weather_main_types WHERE main_name = 'Snow'), 'light shower snow', (SELECT icons_id FROM weather_icons WHERE icon_code = '13d')),
(621, (SELECT main_id FROM weather_main_types WHERE main_name = 'Snow'), 'shower snow', (SELECT icons_id FROM weather_icons WHERE icon_code = '13d')),
(622, (SELECT main_id FROM weather_main_types WHERE main_name = 'Snow'), 'heavy shower snow', (SELECT icons_id FROM weather_icons WHERE icon_code = '13d')),

-- Mist, Fog, Dust и др.
(701, (SELECT main_id FROM weather_main_types WHERE main_name = 'Mist'), 'mist', (SELECT icons_id FROM weather_icons WHERE icon_code = '50d')),
(711, (SELECT main_id FROM weather_main_types WHERE main_name = 'Smoke'), 'smoke', (SELECT icons_id FROM weather_icons WHERE icon_code = '50d')),
(721, (SELECT main_id FROM weather_main_types WHERE main_name = 'Haze'), 'haze', (SELECT icons_id FROM weather_icons WHERE icon_code = '50d')),
(731, (SELECT main_id FROM weather_main_types WHERE main_name = 'Dust'), 'sand/dust whirls', (SELECT icons_id FROM weather_icons WHERE icon_code = '50d')),
(741, (SELECT main_id FROM weather_main_types WHERE main_name = 'Fog'), 'fog', (SELECT icons_id FROM weather_icons WHERE icon_code = '50d')),
(751, (SELECT main_id FROM weather_main_types WHERE main_name = 'Sand'), 'sand', (SELECT icons_id FROM weather_icons WHERE icon_code = '50d')),
(761, (SELECT main_id FROM weather_main_types WHERE main_name = 'Dust'), 'dust', (SELECT icons_id FROM weather_icons WHERE icon_code = '50d')),
(762, (SELECT main_id FROM weather_main_types WHERE main_name = 'Ash'), 'volcanic ash', (SELECT icons_id FROM weather_icons WHERE icon_code = '50d')),
(771, (SELECT main_id FROM weather_main_types WHERE main_name = 'Squall'), 'squalls', (SELECT icons_id FROM weather_icons WHERE icon_code = '50d')),
(781, (SELECT main_id FROM weather_main_types WHERE main_name = 'Tornado'), 'tornado', (SELECT icons_id FROM weather_icons WHERE icon_code = '50d')),

-- Clear
(800, (SELECT main_id FROM weather_main_types WHERE main_name = 'Clear'), 'clear sky', (SELECT icons_id FROM weather_icons WHERE icon_code = '01d')),

-- Clouds
(801, (SELECT main_id FROM weather_main_types WHERE main_name = 'Clouds'), 'few clouds: 11-25%', (SELECT icons_id FROM weather_icons WHERE icon_code = '02d')),
(802, (SELECT main_id FROM weather_main_types WHERE main_name = 'Clouds'), 'scattered clouds: 25-50%', (SELECT icons_id FROM weather_icons WHERE icon_code = '03d')),
(803, (SELECT main_id FROM weather_main_types WHERE main_name = 'Clouds'), 'broken clouds: 51-84%', (SELECT icons_id FROM weather_icons WHERE icon_code = '04d')),
(804, (SELECT main_id FROM weather_main_types WHERE main_name = 'Clouds'), 'overcast clouds: 85-100%', (SELECT icons_id FROM weather_icons WHERE icon_code = '04d'));


INSERT INTO "country" ("name")
VALUES
    ('Russia'),
    ('United Kingdom');

INSERT INTO cities (name, country, lat, lon)
VALUES
    ('Vladivostok', (SELECT "id" FROM "country" WHERE "name" = 'Russia'), 43.115540, 131.885498),
    ('Moscow',      (SELECT "id" FROM "country" WHERE "name" = 'Russia'), 55.755826, 37.617300),
    ('London',      (SELECT "id" FROM "country" WHERE "name" = 'United Kingdom'), 51.507351, -0.127758);