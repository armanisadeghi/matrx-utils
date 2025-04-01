import os

def sample_directory_creation():
    # Base path up to where the directories need to be created
    base_path = r"D:\OneDrive\dev\PycharmProjects\aidream\temp"

    # Directory paths to be created
    directories = [
        os.path.join(base_path, 'code_gen_saves', 'typescript'),
        os.path.join(base_path, 'code_gen_saves', 'redux')
    ]

    for full_path in directories:
        try:
            print(f"Attempting to create directory: {full_path}")
            os.makedirs(full_path, exist_ok=True)
            print(f"Directory created successfully or already exists: {full_path}")
        except Exception as e:
            print(f"An error occurred while creating {full_path}: {str(e)}")

sample_directory_creation()
