
INSERT INTO "country" ("name")
VALUES
    ('Russia'),
    ('United Kingdom');

INSERT INTO cities (name, country, lat, lon)
VALUES
    ('Vladivostok', (SELECT "id" FROM "country" WHERE "name" = 'Russia'), 43.115540, 131.885498),
    ('Moscow',      (SELECT "id" FROM "country" WHERE "name" = 'Russia'), 55.755826, 37.617300),
    ('London',      (SELECT "id" FROM "country" WHERE "name" = 'United Kingdom'), 51.507351, -0.127758);

