-- Validate legacy DD/MM/YYYY values before changing the column type.
-- This query should return no rows. Fix any returned values before continuing.
SELECT id, nombre, fecha
FROM kids
WHERE fecha IS NULL
   OR fecha !~ '^\d{2}/\d{2}/\d{4}$'
   OR to_char(to_date(fecha, 'DD/MM/YYYY'), 'DD/MM/YYYY') <> fecha;

-- Convert existing values in place without deleting or recreating rows.
ALTER TABLE kids
ALTER COLUMN fecha TYPE DATE
USING to_date(fecha, 'DD/MM/YYYY');
