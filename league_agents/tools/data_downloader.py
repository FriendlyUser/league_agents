import os
import time
from datetime import datetime, timedelta
import gdown

LEAGUE_FILE_PATH = 'league_pro_games.csv' # Defined as a global constant


def is_file_updated_within_24_hours(file_path):
    """
    Checks if a file at the given path has been modified within
    the last 24 hours.

    Args:
        file_path (str): The path to the file.

    Returns:
        bool: True if the file exists and has been updated within
              the last 24 hours, False otherwise.
    """
    if os.path.exists(file_path):
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        return datetime.now() - file_mod_time < timedelta(hours=24)
    return False


def download_csv(file_path=LEAGUE_FILE_PATH):
    """
    Downloads the CSV file from Google Drive if the local file has not
    been updated within the last 24 hours. Otherwise, it skips downloading.
    The downloaded file is saved to `file_path`.
    """
    file_url = 'https://drive.google.com/uc?id=1v6LRphp2kYciU4SXp0PCjEMuev1bDejc'  # Updated file ID

    if not is_file_updated_within_24_hours(file_path):
        gdown.download(file_url, file_path, quiet=False)
        print("File downloaded successfully.")
    else:
        print("File is up to date.")


if __name__ == '__main__':
    download_csv()  # Example usage: Downloads if needed when run directly