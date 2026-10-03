import os
from dotenv import load_dotenv
from supabase import create_client, Client



load_dotenv()

# get Supabase env vars
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_KEY or not SUPABASE_URL:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables.")


supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

