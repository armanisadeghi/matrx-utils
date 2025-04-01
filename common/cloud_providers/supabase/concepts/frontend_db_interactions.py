from common import pretty_print
from common.supabase.supabase_client import get_supabase_client


def get_chat_history():
    supabase = get_supabase_client()
    response = supabase.table('chats').select("*").execute()

    return response.data


def get_chat_by_id(chat_id: str):
    supabase = get_supabase_client()
    response = supabase.table('chats').select("*").eq("chat_id", chat_id).single().execute()
    if response.error:
        raise Exception(response.error)
    return response.data

def get_user_chats(user_id: str):
    supabase = get_supabase_client()
    response = supabase.table('chats').select("*").eq("user_id", user_id).execute()
    if response.error:
        raise Exception(response.error)
    return response.data


all_chats = get_chat_history()

pretty_print(all_chats)
