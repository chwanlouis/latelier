import os
import zipfile
import requests
from pathlib import Path
from tqdm import tqdm
from tools.log import logger

DATASET_URL = "https://foodb.ca/public/system/downloads/foodb_2020_04_07_json.zip"


def download_and_extract_foodb(target_dir: str = "backend/data/foodb"):
    """
    Streams the massive FooDB zip archive from the official repo,
    saves it to an ignored temp file, and extracts the raw JSON records.
    """
    # 1. Establish absolute file path references outside git staging area
    base_path = Path(__file__).resolve().parents[2]  # Navigates to project root
    output_dir = base_path / target_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    zip_file_path = output_dir / "foodb_latest.zip"

    logger.info(f"Target distribution path verified: {output_dir}")

    # 2. Open stream request to prevent high RAM inflation spikes
    logger.info(f"Connecting to data host source: {DATASET_URL}")
    response = requests.get(DATASET_URL, stream=True)
    response.raise_for_status()

    total_size_bytes = int(response.headers.get('content-length', 0))
    chunk_size = 1024 * 1024  # Process stream in comfortable 1MB chunks

    # 3. Stream file writes directly to disc with interactive console track
    logger.info(f"Downloading dataset archive ({total_size_bytes / (1024 * 1024):.2f} MB)...")
    with open(zip_file_path, "wb") as f, tqdm(
            total=total_size_bytes,
            unit="iB",
            unit_scale=True,
            desc="FooDB Download"
    ) as progress_bar:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                progress_bar.update(len(chunk))

    # 4. Extract content and purge compressed zip artifact safely
    logger.info("Decompressing raw source file arrays to JSON targets...")
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        # Extract files straight into the target ignored directory context
        zip_ref.extractall(output_dir)

    logger.info("Cleaning up compressed storage fragments...")
    os.remove(zip_file_path)

    logger.info(f"FooDB data migration complete! All files ready inside: {output_dir}")


if __name__ == "__main__":
    download_and_extract_foodb()