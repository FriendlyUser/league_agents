from googleapiclient.discovery import build
import re
import json
import os
import csv
import os
import requests
from youtube_transcript_api import YouTubeTranscriptApi

def extract_teams(input_str):
    # Split the string up to the first "|"
    first_part = input_str.split("|")[0].strip()
    
    # Remove the word "vs" or "vs." and trim whitespace
    teams = first_part.replace("vs.", "").replace("vs", "").strip()
    
    # Split by any remaining whitespace to get individual team names
    team_names = teams.split()
    
    return tuple(team_names)

# download the transcript, then apply the llm analysis to it, cut into early game
# mid game and late game
# def download_file_from_private_repo(file_url, access_token, destination_path):
#     headers = {'Authorization': f'token {access_token}'}
#     response = requests.get(file_url, headers=headers)

#     if response.status_code == 200:
#         with open(destination_path, 'w') as file:
#             file.write(response.text)
#         print("File downloaded successfully.")
#     else:
#         print(f"Failed to download file: {response.status_code}")

# # Example usage
# ACCESS_TOKEN = 'your_github_access_token_here'
# FILE_URL = 'https://raw.githubusercontent.com/username/repository/branch/path/to/your/file.txt'
# DESTINATION_PATH = 'path/to/save/your/file.txt'

# function that I could use for the deno deploy client side
def find_interview_and_condense(youtube_data):
    # Calculate the 80% index mark to determine if the 'interview' mention is past this point.
    eighty_percent_mark = int(len(youtube_data) * 0.8)
    
    # Iterate over the youtube data to find the first index of 'interview' mention.
    for index, entry in enumerate(youtube_data):
        if 'interview' in entry['text'].lower():
            # If the 'interview' mention is past the 80% mark of the entries, return the condensed array.
            if index >= eighty_percent_mark:
                return youtube_data[index:], index
            break

# Fetch the API key from environment variables
developer_key = os.environ.get("YOUTUBE_API_KEY")

# channel_name = "lolesportsvods"
channel_name = '@LCKglobal'

print("developer_key", developer_key)
# if developer_key is None: throw error
if developer_key is None:
    print("Error: YOUTUBE_API_KEY environment variable is not set.")
    exit(1)
# Step 1: Find the channel ID
search_url = "https://www.googleapis.com/youtube/v3/search"
params_channel = {
    "part": "id,snippet",
    "q": channel_name,
    "type": "channel",
    "maxResults": 100,
    "key": developer_key,
}

channel_response = requests.get(search_url, params=params_channel).json()

print("Channel found:", channel_response)
channel_id = channel_response["items"][0]["id"]["channelId"]

# (Optional) Regex pattern for matching your highlight titles
pattern = r"^(?!.*Game \d+).*vs.*\|.*Highlight"

# Step 2: Search for highlight videos in the channel
query = "vs 2025 Highlights"

params_videos = {
    "part": "id,snippet",
    "channelId": channel_id,
    "q": query,
    "type": "video",
    "maxResults": 1000,
    "key": developer_key,
}

videos_response = requests.get(search_url, params=params_videos).json()




csv_file_path = os.path.join("data", "match_data.csv")
existing_video_ids = set()

try:
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            existing_video_ids.add(row['videoID'])
except FileNotFoundError:
    print("CSV file not found, will be created.")

matched_items = []
for video in videos_response['items']:
    video_id = video['id']['videoId']
    video_title = video['snippet']['title']
    
    # Check if the videoID is already in the CSV, skip if it exists
    if video_id not in existing_video_ids:
        # if re.match(pattern, video_title):  # Assuming `pattern` is previously defined
        # if we cant extract the team names just throw an error
        try:
            teams = extract_teams(video_title)
            print(teams)
            team_1 = teams[0]
            team_2 = teams[1]
            matched_items.append(video)
        except Exception as e:
            print(f"Error processing video title: {video_title}. Error: {e}")
            print(video)
            exit(1)

# Open the CSV file in append mode ('a') so we don't overwrite existing data
with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
    # Define the CSV writer
    csvwriter = csv.writer(csvfile)
    
    # Check if the file is empty to write headers
    if csvfile.tell() == 0:
        csvwriter.writerow(['team1', 'team2', 'videoTitle', 'videoID', 'uploadDate'])
    
    # Loop through each video item
    for video in matched_items:
        video_id = video['id']['videoId']
        video_title = video['snippet']['title']
        upload_date = video['snippet']['publishedAt']  # Assuming this is where upload date is
        
        # Extract team names from the video title (customize this based on your video title structure)
        teams = extract_teams(video_title)
        if len(teams) != 2:
            team_1 = teams[0]
            team_2 = teams[1]
        else:
            teams_1, teams_2 = teams
        
        # Write the data to the CSV
        csvwriter.writerow([team_1, team_2, video_title, video_id, upload_date])
    else:
        print("no new matches found")

exit(1)  
# make a simple csv that contains, title, extract team t1,t2 from title and then save as pandas dataframe
for video in matched_items:
    video_id = video['id']['videoId']
    # todo dont think I need this here
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    transcript = transcript_list.find_generated_transcript(['en'])
    transcript_data = transcript.fetch()
    video_title = video['snippet']['title'].replace("|", "")
    with open(f'data/vods/{video_title}.json', 'w') as f:
        json.dump(transcript_data, f)
