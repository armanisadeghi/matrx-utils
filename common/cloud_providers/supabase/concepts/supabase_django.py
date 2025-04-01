import os
from supabase import create_client, Client
import dotenv


dotenv.load_dotenv()

def get_supabase_client():
    url: str = os.environ.get("SUPABASE_DJANGO_URL")
    key: str = os.environ.get("SUPABASE_DJANGO_KEY")
    supabase: Client = create_client(url, key)
    return supabase
