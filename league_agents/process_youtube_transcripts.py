from googleapiclient.discovery import build
import re
import json
import os
import csv
import os
import requests
from youtube_transcript_api import YouTubeTranscriptApi

# Creating a flat list with 2 or 3 letter abbreviations for each team

lpl_team_abbreviations = [
    "OMG",  # Oh My God
    "WBG",  # Weibo Gaming
    "TT",   # ThunderTalk Gaming
    "LNG",  # LNG Esports
    "RNG",  # Royal Never Give Up
    "FPX",  # FunPlus Phoenix
    "UP",   # Ultra Prime
    "LGD",  # LGD Gaming
    "AL",   # Anyone's Legend
    "BLG",  # Bilibili Gaming
    "EDG",  # EDward Gaming
    "TES",  # Top Esports
    "WE",   # Team WE
    "iG",   # Invictus Gaming
    "NIP",  # Ninjas in Pyjamas.CN
    "JDG"   # JD Gaming
]




def extract_teams_new(input_str):
    # find teams in teams_abbreviations
    teams = [team for team in lpl_team_abbreviations if team in input_str]
    # limit to 2 entries
    teams = teams[:2]
    return tuple(teams)

def extract_teams(input_str):
    # Split the string up to the first "|"
    first_part = input_str.split("|")[0].strip()
    
    # Remove the word "vs" or "vs." and trim whitespace
    teams = first_part.replace("vs.", "").replace("vs", "").strip()
    
    # Split by any remaining whitespace to get individual team names
    team_names = teams.split()

    print(team_names)
    
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
channel_name = 'LPL_ENGLISH'

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

# print("Channel found:", channel_response)
channel_id = channel_response["items"][0]["id"]["channelId"]

# (Optional) Regex pattern for matching your highlight titles
pattern = r"vs"

# Step 2: Search for highlight videos in the channel
query = "LPL 2025"
# date cutoff
date_cutoff = "2025-01-10T00:00:00Z"
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


from datetime import timedelta

def format_srt_timestamp(seconds: float) -> str:
    """Converts seconds to SRT timestamp format (HH:MM:SS,mmm)."""
    time_delta = timedelta(seconds=int(seconds))
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def convert_transcript_to_srt(transcript: list) -> str:
    """Converts a list of transcript entries into SRT format."""
    srt_output = []
    for index, entry in enumerate(transcript, start=1):
        start_time = format_srt_timestamp(entry['start'])
        end_time = format_srt_timestamp(entry['start'] + entry['duration'])
        text = entry['text']
        
        srt_output.append(f"{start_time} --> {end_time}\n{text}\n")
    
    return "\n".join(srt_output)


import os
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate

def analyze_esports_match(video_title: str, video_transcript: str) -> str:
    """
    Reads in the team data from data/lpl_teams_2025.md and sets up a LangChain LLM chain
    that uses a prompt with the provided video title, transcript, and team data to generate
    an analysis of the esports match.
    
    The prompt instructs the LLM to act as an esports analyst and use the team rosters
    (provided in the markdown file) to correct typos in player names and give a detailed breakdown
    of each player's performance.
    
    Parameters:
        video_title (str): The title of the YouTube video.
        video_transcript (str): The full transcript of the video.
        
    Returns:
        str: The generated analysis of the match.
    """
    # Import the team data from the markdown file
    teams_data_path = "data/lpl_teams_2025.md"
    with open(teams_data_path, "r", encoding="utf-8") as file:
        teams_data = file.read()

    # Define the prompt template with placeholders for the video title, transcript, and teams data.
    prompt_template = """
Act as an esports analyst. Given the following transcript of the esports game titled "{video_title}", determine how close the matches were. 
You will also be provided the team names and roster. Use that to accurately describe the performance of the players, and correct any typos in the player names.

Team Data:
{teams_data}

Transcript:
{video_transcript}

Provide a detailed breakdown of each player's performance as well as an overall analysis of the game.
    """

    prompt_template_filtering = """
        Given the following video title on youtube "{video_title}" and the full list of teams in league of legends with their players.
        We want to return the list of players and their team members:
        {teams_data}

        For example: for the title LPL 2025 WBG vs JDG | BO5 FEARLESS

        Return:

        JDG (JD Gaming)
            - Ale
            - Xun
            - Scout
            - Peyz
            - MISSING
            - cvMax
            - BoBo

        ## WBG (Weibo Gaming)
            - Breathe
            - Tian
            - Xiaohu
            - Light
            - Hang
            - NoFe
            - Tselin

    """
    clean_prompt = PromptTemplate(
        input_variables=["video_title",  "teams_data"],
        template=prompt_template_filtering
    )
    # Create the prompt template for LangChain
    prompt = PromptTemplate(
        input_variables=["video_title", "video_transcript", "teams_data"],
        template=prompt_template
    )

    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

    llm = GoogleGenerativeAI(model="gemini-2.0-flash", api_key=GOOGLE_API_KEY)

    # Run the chain with the provided inputs
    # chain = clean_prompt | prompt | llm

    valid_chain = clean_prompt | llm
    prompt_chain = prompt | llm
    valid_teams = valid_chain.invoke(input={
        "video_title": video_title,
        "teams_data": teams_data})

    srt_transcript = convert_transcript_to_srt(video_transcript)

    analysis = prompt_chain.invoke(input={
        "video_title": video_title,
        "video_transcript": srt_transcript,
        "teams_data": valid_teams
    })

    # write to file  data lpl_summaries
    summary_file_path = os.path.join("data", "lpl_summaries.txt")
    with open(summary_file_path, "a", encoding="utf-8") as file:
        file.write(video_title + "\n" + analysis + "\n" + "\n")
    
    return analysis


#
matched_items = []
for video in videos_response['items']:
    video_id = video['id']['videoId']
    video_title = video['snippet']['title']
    
    # Check if the videoID is already in the CSV, skip if it exists
    if video_id not in existing_video_ids:
        # if re.match(pattern, video_title):  # Assuming `pattern` is previously defined
        # if we cant extract the team names just throw an error
        # return if not past cutoff date
        if video['snippet']['publishedAt'] < date_cutoff:
            print("skipping video published before cutoff date: ", video['snippet']['publishedAt'])
            continue
        try:
            # if missing vs continue
            if "vs" not in video_title.lower():
                print("skipping video missing vs: ", video_title)
                continue
            if query not in video_title:
                print("skipping video missing query: ", video_title)
                continue
            print("processing video: ", video_title)
            # teams = extract_teams_new(video_title)
            # team_1 = teams[0]
            # team_2 = teams[1]
            matched_items.append(video)
        except Exception as e:
            print(f"Error processing video title: {video_title}. Error: {e}")
            print(video)

# make a simple csv that contains, title, extract team t1,t2 from title and then save as pandas dataframe
for video in matched_items:
    video_id = video['id']['videoId']
    video_title = video['snippet']['title']
    # todo dont think I need this here
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    transcript = transcript_list.find_generated_transcript(['en'])
    transcript_data = transcript.fetch()

    analyze_esports_match(video_title, transcript_data)
