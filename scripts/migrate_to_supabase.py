"""
One-time script: links existing images in the Supabase Storage bucket
to their corresponding rows in the kids table (sets image_url).

Run this after kids.sql has been executed and images have been uploaded manually.

Usage:
    SUPABASE_URL=https://tgemfmlgirdpizhpqshf.supabase.co \
    SUPABASE_SERVICE_ROLE_KEY=... \
    python scripts/migrate_to_supabase.py
"""
import os
import sys
import unicodedata

from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY env vars")
    sys.exit(1)

client = create_client(SUPABASE_URL, SUPABASE_KEY)


def normalize(nombre: str) -> str:
    nfkd = unicodedata.normalize("NFD", nombre.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


# List files in the bucket
files = client.storage.from_("images").list()
bucket_files = {f["name"] for f in files}
print(f"Bucket 'images': {len(bucket_files)} files found")
if bucket_files:
    print(f"  Sample: {list(bucket_files)[:3]}")

# Load all kids from DB
kids = client.table("kids").select("nombre").execute().data
print(f"Table 'kids': {len(kids)} rows found")

updated = 0
skipped = 0
for kid in kids:
    nombre = kid["nombre"]
    filename = f"{normalize(nombre)}.jpeg"

    if filename not in bucket_files:
        print(f"  - {nombre}: no image in bucket ({filename})")
        skipped += 1
        continue

    public_url = client.storage.from_("images").get_public_url(filename)
    client.table("kids").update({"image_url": public_url}).eq("nombre", nombre).execute()
    print(f"  ✓ {nombre} → {public_url}")
    updated += 1

print(f"\nDone: {updated} linked, {skipped} without image.")
