-- Run this in the Supabase SQL editor (dashboard → SQL Editor → New query)

CREATE TABLE IF NOT EXISTS kids (
  id        SERIAL PRIMARY KEY,
  nombre    TEXT    NOT NULL,
  fecha     DATE    NOT NULL,
  clan      TEXT    NOT NULL,
  embarazo  BOOLEAN NOT NULL DEFAULT FALSE,
  image_url TEXT
);

-- Unique constraint so upserts work on nombre
ALTER TABLE kids ADD CONSTRAINT kids_nombre_unique UNIQUE (nombre);

-- Seed data (mirrors data.json)
INSERT INTO kids (nombre, fecha, clan) VALUES
  ('Marta',    '2017-09-25', 'mc'),
  ('Mateo',    '2018-08-28', 'mc'),
  ('Lucas',    '2018-10-10', 'cm'),
  ('Clara',    '2019-05-18', 'cf'),
  ('Juan',     '2019-12-10', 'cc'),
  ('Catalina', '2019-12-14', 'mc'),
  ('Javier',   '2020-12-18', 'cf'),
  ('Raquel',   '2021-05-19', 'cm'),
  ('Sofía',    '2021-06-28', 'mtc'),
  ('Tomás',    '2021-07-09', 'cc'),
  ('Carlos',   '2022-07-10', 'mtc'),
  ('Paula',    '2022-09-17', 'mc'),
  ('Rodrigo',  '2022-10-29', 'cc'),
  ('Bruno',    '2023-08-01', 'cm'),
  ('Marc',     '2023-08-13', 'mtc'),
  ('Blanca',   '2024-01-12', 'cc'),
  ('Míriam',   '2024-04-14', 'mc'),
  ('Andreu',   '2024-05-31', 'cf'),
  ('Pedro',    '2025-02-09', 'mtc'),
  ('Inés',     '2025-07-13', 'cf'),
  ('María',    '2025-09-04', 'cc'),
  ('Joan',     '2026-06-28', 'mtc')
ON CONFLICT (nombre) DO NOTHING;
