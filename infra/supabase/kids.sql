-- Run this in the Supabase SQL editor (dashboard → SQL Editor → New query)

CREATE TABLE IF NOT EXISTS kids (
  id        SERIAL PRIMARY KEY,
  nombre    TEXT    NOT NULL,
  fecha     TEXT    NOT NULL,  -- DD/MM/YYYY
  clan      TEXT    NOT NULL,
  embarazo  BOOLEAN NOT NULL DEFAULT FALSE,
  image_url TEXT
);

-- Unique constraint so upserts work on nombre
ALTER TABLE kids ADD CONSTRAINT kids_nombre_unique UNIQUE (nombre);

-- Seed data (mirrors data.json)
INSERT INTO kids (nombre, fecha, clan) VALUES
  ('Marta',    '25/09/2017', 'mc'),
  ('Mateo',    '28/08/2018', 'mc'),
  ('Lucas',    '10/10/2018', 'cm'),
  ('Clara',    '18/05/2019', 'cf'),
  ('Juan',     '10/12/2019', 'cc'),
  ('Catalina', '14/12/2019', 'mc'),
  ('Javier',   '18/12/2020', 'cf'),
  ('Raquel',   '19/05/2021', 'cm'),
  ('Sofía',    '28/06/2021', 'mtc'),
  ('Tomás',    '09/07/2021', 'cc'),
  ('Carlos',   '10/07/2022', 'mtc'),
  ('Paula',    '17/09/2022', 'mc'),
  ('Rodrigo',  '29/10/2022', 'cc'),
  ('Bruno',    '01/08/2023', 'cm'),
  ('Marc',     '13/08/2023', 'mtc'),
  ('Blanca',   '12/01/2024', 'cc'),
  ('Míriam',   '14/04/2024', 'mc'),
  ('Andreu',   '31/05/2024', 'cf'),
  ('Pedro',    '09/02/2025', 'mtc'),
  ('Inés',     '13/07/2025', 'cf'),
  ('María',    '04/09/2025', 'cc'),
  ('Joan',     '28/06/2026', 'mtc')
ON CONFLICT (nombre) DO NOTHING;
