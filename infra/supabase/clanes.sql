-- Run this in the Supabase SQL editor for a new installation.

CREATE TABLE IF NOT EXISTS clanes (
  clan      TEXT PRIMARY KEY,
  clan_name TEXT NOT NULL
);

INSERT INTO clanes (clan, clan_name) VALUES
  ('cm',  'Codina Martínez'),
  ('mc',  'Marín Codina'),
  ('cc',  'Cudina Codina'),
  ('cf',  'Codina Ferreres'),
  ('mtc', 'Martín Codina')
ON CONFLICT (clan) DO NOTHING;
