import os
import requests


folder_path = '../data/recipes'
file_name = "le_guide_culinaire_escoffier.txt"
escoffier_file_path = os.path.join(folder_path, file_name)


def download_book_escoffier():
    download_url = "https://www.gutenberg.org/cache/epub/71395/pg71395.txt"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")

    if not os.path.exists(escoffier_file_path):
        print(f"File '{file_name}' not found in '{folder_path}'. Downloading from {download_url}...")
        try:
            response = requests.get(download_url)
            response.raise_for_status()
            with open(escoffier_file_path, 'wb') as f:
                f.write(response.content)
            print(f"Download complete. File saved as '{escoffier_file_path}'.")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading file: {e}")
    else:
        print(f"File '{file_name}' already exists in '{folder_path}'. Skipping download.")