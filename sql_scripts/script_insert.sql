INSERT INTO weather_observations
    (city_id, condition_id, temp, temp_min, temp_max, pressure, humidity,
    visibility, wind_speed, wind_deg, clouds_all, recorded_at, sunrise, sunset)
VALUES ((SELECT city_id from cities where name = %s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
RETURNING weather_observations_id