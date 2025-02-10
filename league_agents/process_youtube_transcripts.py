#!/usr/bin/env python3
import argparse
import csv
import os
import re
import requests
from datetime import timedelta
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate

# --- Global Data and Helper Functions ---

# A list of team abbreviations used for potential team extraction.
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

def extract_teams_new(input_str: str):
    """
    Given an input string, return a tuple of at most two team abbreviations
    found in the string.
    """
    teams = [team for team in lpl_team_abbreviations if team in input_str]
    return tuple(teams[:2])

def extract_teams(input_str: str):
    """
    Extract team names from a string by splitting the first section
    before the "|" character and removing any 'vs' text.
    """
    first_part = input_str.split("|")[0].strip()
    teams = first_part.replace("vs.", "").replace("vs", "").strip()
    team_names = teams.split()
    print("Extracted teams:", team_names)
    return tuple(team_names)

def find_interview_and_condense(youtube_data):
    """
    Checks for the word 'interview' in the transcript entries and returns
    a condensed transcript if the mention occurs past 80% of the content.
    """
    eighty_percent_mark = int(len(youtube_data) * 0.8)
    for index, entry in enumerate(youtube_data):
        if 'interview' in entry['text'].lower():
            if index >= eighty_percent_mark:
                return youtube_data[index:], index
            break

def format_srt_timestamp(seconds: float) -> str:
    """
    Converts a time value in seconds to SRT timestamp format (HH:MM:SS,mmm).
    """
    time_delta = timedelta(seconds=int(seconds))
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def convert_transcript_to_srt(transcript: list) -> str:
    """
    Converts a transcript (a list of entries with 'start', 'duration', and 'text')
    into a string formatted as SRT subtitles.
    """
    srt_output = []
    for index, entry in enumerate(transcript, start=1):
        start_time = format_srt_timestamp(entry['start'])
        end_time = format_srt_timestamp(entry['start'] + entry['duration'])
        text = entry['text']
        srt_output.append(f"{start_time} --> {end_time}\n{text}\n")
    return "\n".join(srt_output)

def analyze_esports_match(video_title: str, video_transcript: list, google_api_key: str) -> str:
    """
    Uses LangChain and Google Generative AI to analyze an esports match.
    The function reads in team roster data from a local markdown file, creates
    prompt templates, and then uses the LLM to first validate team information
    and then to generate a detailed match analysis.
    
    Parameters:
      video_title: Title of the YouTube video.
      video_transcript: Transcript data (list of dict entries) from the video.
      google_api_key: API key for Google Generative AI.
    
    Returns:
      A string containing the analysis of the match.
    """
    # Load team data from a markdown file.
    teams_data_path = "data/lpl_teams_2025.md"
    try:
        with open(teams_data_path, "r", encoding="utf-8") as file:
            teams_data = file.read()
    except FileNotFoundError:
        print(f"Error: Team data file not found at {teams_data_path}")
        return "Team data file missing."

    # Prompt to validate or filter team data.
    prompt_template_filtering = """
Given the following video title on YouTube "{video_title}" and the full list of teams in League of Legends with their players,
return the list of players grouped by their team. For example, for the title:
    
    LPL 2025 WBG vs JDG | BO5 FEARLESS

Return something like:

    JDG (JD Gaming)
        - Ale
        - Xun
        - Scout
        - Peyz
        - MISSING
        - cvMax
        - BoBo

    WBG (Weibo Gaming)
        - Breathe
        - Tian
        - Xiaohu
        - Light
        - Hang
        - NoFe
        - Tselin
       
Teams Data:
{teams_data}
    """
    # Main prompt for match analysis.
    prompt_template = """
Act as an esports analyst. Given the following transcript of the esports game titled "{video_title}", determine how close the match was.
Use the team names and rosters provided to accurately describe each player's performance and correct any typos in player names.

Team Data:
{teams_data}

Transcript:
{video_transcript}

Provide a detailed breakdown of each player's performance as well as an overall analysis of the game. Note what the final score between teams is.

Also identify what each team did well and poorly.
    """

    # Set up LangChain prompt templates.
    clean_prompt = PromptTemplate(
        input_variables=["video_title", "teams_data"],
        template=prompt_template_filtering
    )
    prompt = PromptTemplate(
        input_variables=["video_title", "video_transcript", "teams_data"],
        template=prompt_template
    )

    # Initialize the LLM client.
    llm = GoogleGenerativeAI(model="gemini-2.0-flash", api_key=google_api_key)

    # First, obtain validated team data.
    valid_chain = clean_prompt | llm
    valid_teams = valid_chain.invoke(input={
        "video_title": video_title,
        "teams_data": teams_data
    })

    # Convert the transcript to SRT format.
    srt_transcript = convert_transcript_to_srt(video_transcript)

    # Now create the analysis prompt.
    prompt_chain = prompt | llm
    analysis = prompt_chain.invoke(input={
        "video_title": video_title,
        "video_transcript": srt_transcript,
        "teams_data": valid_teams
    })

    return analysis

# --- Main Function ---

def main():
    parser = argparse.ArgumentParser(
        description="Process esports match videos from a YouTube channel and generate match analyses."
    )
    parser.add_argument("--channel", type=str, default="LPL_ENGLISH",
                        help="YouTube channel name to search (default: LPL_ENGLISH)")
    parser.add_argument("--output", type=str, default="data/lpl_summaries.md",
                        help="Output file path for match summaries (default: data/lpl_summaries.md)")
    parser.add_argument("--query", type=str, default="LPL 2025",
                        help="Search query for videos (default: 'LPL 2025')")
    parser.add_argument("--date_cutoff", type=str, default="2025-01-10T00:00:00Z",
                        help="ISO date cutoff; skip videos published before this (default: 2025-01-10T00:00:00Z)")
    parser.add_argument("--csv_file", type=str, default="data/match_data.csv",
                        help="CSV file to store processed video IDs (default: data/match_data.csv)")
    args = parser.parse_args()

    channel_name = args.channel
    output_file_path = args.output
    query = args.query
    date_cutoff = args.date_cutoff
    csv_file_path = args.csv_file

    # Retrieve API keys from the environment.
    developer_key = os.environ.get("YOUTUBE_API_KEY")
    if not developer_key:
        print("Error: YOUTUBE_API_KEY environment variable is not set.")
        exit(1)
    google_api_key = os.environ.get("GOOGLE_API_KEY")
    if not google_api_key:
        print("Error: GOOGLE_API_KEY environment variable is not set.")
        exit(1)

    print("Using channel:", channel_name)
    print("Developer key loaded.")

    # Step 1: Find the channel ID using the YouTube API.
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params_channel = {
        "part": "id,snippet",
        "q": channel_name,
        "type": "channel",
        "maxResults": 100,
        "key": developer_key,
    }
    channel_response = requests.get(search_url, params=params_channel).json()
    if not channel_response.get("items"):
        print("No channel found for", channel_name)
        exit(1)
    channel_id = channel_response["items"][0]["id"]["channelId"]
    print("Found channel ID:", channel_id)

    # Step 2: Search for videos in the channel matching the query.
    params_videos = {
        "part": "id,snippet",
        "channelId": channel_id,
        "q": query,
        "type": "video",
        "maxResults": 50,
        "key": developer_key,
    }
    videos_response = requests.get(search_url, params=params_videos).json()
    if not videos_response.get("items"):
        print("No videos found with query", query)
        exit(1)

    # Step 3: Load any existing video IDs from the CSV to avoid duplicate processing.
    existing_video_ids = set()
    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                existing_video_ids.add(row['videoID'])
    except FileNotFoundError:
        print("CSV file not found, it will be created.")

    # Step 4: Filter videos based on publication date, presence of "vs", and query text.
    matched_items = []
    for video in videos_response.get('items', []):
        video_id = video['id']['videoId']
        video_title = video['snippet']['title']
        published_at = video['snippet']['publishedAt']
        if video_id in existing_video_ids:
            continue
        if published_at < date_cutoff:
            print("Skipping video published before cutoff:", published_at)
            continue
        if "vs" not in video_title.lower():
            print("Skipping video missing 'vs' in title:", video_title)
            continue
        if query not in video_title:
            print("Skipping video missing query text in title:", video_title)
            continue
        print("Processing video:", video_title)
        matched_items.append(video)

    # Step 5: Process each matched video.
    for video in matched_items:
        video_id = video['id']['videoId']
        video_title = video['snippet']['title']
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_generated_transcript(['en'])
            transcript_data = transcript.fetch()
        except Exception as e:
            print(f"Error fetching transcript for video {video_title} ({video_id}): {e}")
            continue

        # Generate the match analysis.
        analysis = analyze_esports_match(video_title, transcript_data, google_api_key)

        # Write the analysis to the output file.
        with open(output_file_path, "a", encoding="utf-8") as out_file:
            out_file.write(video_title + "\n" + analysis + "\n\n")
        print(f"Analysis for '{video_title}' written to {output_file_path}")

if __name__ == '__main__':
    main()
