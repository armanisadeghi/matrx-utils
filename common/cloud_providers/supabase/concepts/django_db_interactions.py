from common import pretty_print
from common.supabase.supabase_django import get_supabase_client


def get_chat_history():
    supabase = get_supabase_client()
    response = supabase.table('chats').select("*").execute()

    return response.data
