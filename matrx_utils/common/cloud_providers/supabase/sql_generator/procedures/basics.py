import os
import json

from dotenv import load_dotenv
from supabase import create_client, Client
load_dotenv()


def main():
    # Load environment variables for Supabase URL and API key
    url = os.getenv("SUPABASE_MATRIX_URL")
    key = os.getenv("SUPABASE_MATRIX_KEY")

    if not url or not key:
        print("Supabase URL or API key not set in environment variables.")
        return

    # Create a Supabase client
    supabase = create_client(url, key)

    # Call the RPC function
    try:
        print("Calling get_schema() RPC function...")
        response = supabase.rpc("get_schema").execute()

        # Directly use the response if it is a dictionary
        if isinstance(response.data, dict):
            schema = response.data
            print("Schema received successfully:")
            print(json.dumps(schema, indent=2))
        elif isinstance(response.data, str):
            # Fallback in case it's a JSON string
            schema = json.loads(response.data)
            print("Schema received successfully:")
            print(json.dumps(schema, indent=2))
        else:
            print("Unexpected response format:", response.data)

    except Exception as e:
        print(f"An error occurred during RPC call: {e}")


if __name__ == "__main__":
    main()
