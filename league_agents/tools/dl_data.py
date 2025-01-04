import gdown
import os
from datetime import datetime, timedelta
import pandas as pd
import os
import google.generativeai as genai

def is_file_updated_within_24_hours(file_path):
    if os.path.exists(file_path):
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        return datetime.now() - file_mod_time < timedelta(hours=24)
    return False


def download_file(output='league_pro_games.csv'):
    
    # drive link for ref https://drive.google.com/drive/u/1/folders/1gLSw0RLjBbtaNy0dgnGQDAZOHIgCe-HH
    # see https://oracleselixir.com/
    # File link
    file_url = 'https://drive.google.com/uc?id=1IjIEhLc9n8eLKeY-yh_YigKVWbhgGBsN'
    # output = 'league_pro_games.csv'  # Change 'downloaded_file.ext' to your desired output file name

    # Download file
    gdown.download(file_url, output, quiet=False)
# we want to 

if __name__ == "__main__":
    local_file = 'league_pro_games.csv'
    # TODO check if file was last updated within 24 hours, else download again
    if not is_file_updated_within_24_hours(local_file):
        download_file(local_file)
    else:
        print("File is already up-to-date, skipping download")