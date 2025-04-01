import json
from pathlib import Path
from .supabase_client import get_supabase_client
from core import BASE_DIR

def upload_to_supabase(input_file, start=0, end=None):
    # Resolve the input file path relative to BASE_DIR
    full_input_path = BASE_DIR / input_file

    # Read the Supabase-ready JSON file
    with open(full_input_path, 'r') as f:
        data = json.load(f)

    # Apply start and end limits
    data_to_upload = data[start:end]

    # Get the Supabase client
    supabase = get_supabase_client()

    # Counter for successful and failed uploads
    success_count = 0
    fail_count = 0

    for item in data_to_upload:
        try:
            # Ensure all fields are present, even if they're None
            supabase_item = {
                "id": item.get("id"),
                "display_name": item.get("display_name"),
                "data_type": item.get("data_type", "str"),
                "description": item.get("description"),
                "official_name": item.get("official_name"),
                "component_type": item.get("component_type"),
                "validation_rules": item.get("validation_rules"),
                "tooltip": item.get("tooltip"),
                "default_value": item.get("default_value"),
                "additional_params": item.get("additional_params", {}),
                "matrix_id": "948387f8-9d11-4c37-a7db-cd2ae112e8d8",
            }

            # Upload the item to the 'broker' table
            response = supabase.table('broker').upsert(supabase_item).execute()

            # Check if the upload was successful
            if response.data:
                success_count += 1
                print(f"Successfully uploaded item with id: {item['id']}")
            else:
                fail_count += 1
                print(f"Failed to upload item with id: {item['id']}")

        except Exception as e:
            fail_count += 1
            print(f"Error uploading item with id: {item['id']}. Error: {str(e)}")

    print(f"\nUpload complete. Successful uploads: {success_count}, Failed uploads: {fail_count}")
    print(f"Uploaded items from index {start} to {end if end is not None else len(data)}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Upload data to Supabase broker table.")
    parser.add_argument("--input", default="temp/oai/MyVariableSerializer_5_supabase.json", help="Path to the input JSON file")
    parser.add_argument("--start", type=int, default=0, help="Start index for upload (default: 0)")
    parser.add_argument("--end", type=int, default=None, help="End index for upload (default: None, meaning all entries)")

    args = parser.parse_args()

    input_file = Path(args.input)
    upload_to_supabase(input_file, start=args.start, end=args.end)
