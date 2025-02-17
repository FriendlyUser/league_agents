import os
import json
import time
import csv
from dotenv import load_dotenv
import requests
import argparse
from datetime import datetime


class YouTubeLiveChat:
    """
    A class to interact with the YouTube Live Chat Messages API.
    """

    def __init__(self, api_key, channel_id=None):
        """
        Initializes the YouTubeLiveChat object.

        Args:
            api_key (str): Your YouTube Data API key.
            channel_id (str, optional): The YouTube channel ID.  Defaults to None.  If None,
                                        channel_id must be set later using `set_channel_id()`.
        """
        self.api_key = api_key
        self.channel_id = channel_id
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.search_url = "https://www.googleapis.com/youtube/v3/search"  # Define search URL
        self.event_details = {}
        self.channel_handle = None

    def set_channel_id(self, channel_id):
        """
        Sets the channel ID after initialization.

        Args:
            channel_id (str): The YouTube channel ID.
        """
        self.channel_id = channel_id

    def find_channel_id_by_name(self, channel_name):
        """
        Finds a channel ID by channel name or handle (@...).

        Args:
            channel_name (str): The name or handle of the YouTube channel.

        Returns:
            str: The channel ID if found, otherwise None.
        """
        params_channel = {
            "part": "id,snippet",
            "q": channel_name,
            "type": "channel",
            "maxResults": 1,  # Reduced to 1 for efficiency (we only need one)
            "key": self.api_key,
        }
        try:
            channel_response = requests.get(
                self.search_url, params=params_channel, verify=True
            ).json()

            if not channel_response.get("items"):
                print(f"No channel found for {channel_name}")
                return None

            self.channel_handle = channel_name  # setting the channel name
            channel_id = channel_response["items"][0]["id"]["channelId"]
            return channel_id

        except requests.exceptions.RequestException as e:
            print(f"Error finding channel ID: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return None
        except KeyError as e:
            print(f"KeyError while parsing channel response: {e}. Check API response format.")
            return None

    def get_live_events(self):
        """
        Retrieves a list of live events for the specified channel.

        Returns:
            list: A list of live event dictionaries, or None if an error occurs.
        """
        if not self.channel_id:
            print(
                "Error: channel_id not set.  Call `set_channel_id()` or `find_channel_id_by_name()` first."
            )
            return None

        url = f"{self.base_url}/search"
        params = {
            "part": "snippet",
            "channelId": self.channel_id,
            "order": "date",
            "type": "video",
            "eventType": "live",  # only return live events
            "key": self.api_key,
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            return data.get("items", [])  # Return an empty list if "items" is not present
        except requests.exceptions.RequestException as e:
            print(f"Error fetching live events: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return None

    def get_live_video_id(self):
        """
        Retrieves the video ID of the currently live event.

        Returns:
            str: The video ID of the live event, or None if no live event is found or an error occurs.
        """
        live_events = self.get_live_events()
        if live_events:
            for event in live_events:
                if event["snippet"]["liveBroadcastContent"] == "live":
                    # we want to set the event details to a property
                    self.event_details = event
                    # we will likely only need description and title
                    # event {'kind': 'youtube#searchResult', 'etag': 'zQTXv8vYwcDtqofXZ-L6ZFYp0P8', 'id': {'kind': 'youtube#video', 'videoId': 'BtEfsZlUHPs'}, 'snippet': {'publishedAt': '2025-02-16T21:43:20Z', 'channelId': 'UCaYLBJfw6d8XqmNlL204lNg', 'title': 'LIVE: PARIVISION vs. AVULUS - DreamLeague Season 25', 'description': 'All about the DreamLeague Season 25 https://dreamhack.com/dreamleague/ Join in the discussion: ...', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/BtEfsZlUHPs/default_live.jpg', 'width': 120, 'height': 90}, 'medium': {'url': 'https://i.ytimg.com/vi/BtEfsZlUHPs/mqdefault_live.jpg', 'width': 320, 'height': 180}, 'high': {'url': 'https://i.ytimg.com/vi/BtEfsZlUHPs/hqdefault_live.jpg', 'width': 480, 'height': 360}}, 'channelTitle': 'ESL Dota 2', 'liveBroadcastContent': 'live', 'publishTime': '2025-02-16T21:43:20Z'}}
                    return event["id"]["videoId"]
        return None

    def get_live_streaming_details(self, video_id):
        """
        Retrieves live streaming details for a given video ID.

        Args:
            video_id (str): The ID of the live video.

        Returns:
            dict: A dictionary containing the live streaming details, or None if an error occurs.
        """
        url = f"{self.base_url}/videos"
        params = {
            "part": "liveStreamingDetails,snippet",
            "id": video_id,
            "key": self.api_key,
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            items = data.get("items")
            if items and len(items) > 0:
                return items[0]  # return the first item
            else:
                print("No live streaming details found for video ID:", video_id)
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching live streaming details: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return None

    def get_active_live_chat_id(self, video_id):
        """
        Retrieves the active live chat ID for a given video ID.

        Args:
            video_id (str): The ID of the live video.

        Returns:
            str: The active live chat ID, or None if not found or an error occurs.
        """
        details = self.get_live_streaming_details(video_id)
        if details and "liveStreamingDetails" in details:
            return details["liveStreamingDetails"].get("activeLiveChatId")
        return None

    def get_live_chat_messages(self, live_chat_id, max_results=2000, page_token=None):
        """
        Retrieves live chat messages for a given live chat ID.

        Args:
            live_chat_id (str): The ID of the live chat.
            max_results (int): The maximum number of messages to retrieve (default: 2000).
            page_token (str, optional): The page token for retrieving the next page of messages. Defaults to None.

        Returns:
            dict: A dictionary containing the live chat messages and polling interval, or None if an error occurs.
        """
        url = f"{self.base_url}/liveChat/messages"
        params = {
            "liveChatId": live_chat_id,
            "part": "snippet,authorDetails",
            "maxResults": max_results,
            "key": self.api_key,
        }
        if page_token:
            params["pageToken"] = page_token

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching live chat messages: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return None

    def poll_live_chat(self, live_chat_id, callback, filename, csv_headers, max_results=2000):
        """
        Polls the live chat for new messages at the interval specified by the API, opening and closing the CSV inside the loop.

        Args:
            live_chat_id (str): The ID of the live chat.
            callback (function): A function to call with the new messages (must accept messages and csv_writer).
            filename (str): The name of the CSV file to write to.
            csv_headers (list): The headers for the CSV file.
            max_results (int): The maximum number of messages to retrieve per poll (default: 2000).
        """
        next_page_token = None
        try:
            csvfile = open(filename, 'a', newline='', encoding='utf-8')  # Open in 'append' mode
            csv_writer = csv.writer(csvfile)

            # Write header only if the file is empty
            if os.stat(filename).st_size == 0:
                csv_writer.writerow(csv_headers)

            while True:
                data = self.get_live_chat_messages(
                    live_chat_id, max_results=max_results, page_token=next_page_token
                )
                if data:
                    messages = data.get("items", [])
                    callback(messages, csv_writer)  # Pass csv_writer to callback
                    next_page_token = data.get("nextPageToken")
                    polling_interval = data.get("pollingIntervalMillis") / 1000  # Convert to seconds
                    time.sleep(polling_interval)  # time sleep function
                else:
                    print("Error occurred while polling.  Stopping.")
                    break  # Exit the loop on error

        except Exception as e:
            print(f"An error occurred during polling: {e}")
        finally:
            if 'csvfile' in locals() and not csvfile.closed: # only closes if csv file is defined and its not already closed
                csvfile.close()
                print(f"CSV file {filename} closed.")


def setup_args():
    """Sets up command-line arguments."""
    parser = argparse.ArgumentParser(description="Fetch YouTube live chat messages and save to CSV.")
    parser.add_argument("--channel_id", help="The YouTube channel ID.")
    parser.add_argument(
        "--channel_name",
        help="The YouTube channel name or handle (e.g., @lolesports).",
        default="@ESLDota2",
    )
    return parser.parse_args()


def process_message(message, csv_writer):
    """Processes a single chat message and writes it to the CSV file."""
    author = message["authorDetails"]["displayName"]
    publishedAt = message["snippet"]["publishedAt"]
    if message["snippet"].get('displayMessage'):
        text = message["snippet"]["displayMessage"]
        csv_writer.writerow([author, text, publishedAt])
    elif message['snippet'].get('type')== 'userBannedEvent':
        print("user banned ignore this message")
    else:
        print("message cannot be processed", message)


def save_messages(messages, csv_writer):
    """Saves a list of messages to the CSV file."""
    for message in messages:
        process_message(message, csv_writer)


def get_filename(youtube_chat):
    """Generates a filename for the CSV file based on channel and video details."""
    channel_name = youtube_chat.channel_handle if youtube_chat.channel_handle else youtube_chat.channel_id
    video_id = youtube_chat.event_details['id']['videoId']
    return f"youtube_chat_{channel_name}_{video_id}.csv"


def ensure_data_directory_exists(directory="data"):
    """Ensures that the specified data directory exists. Creates it if it doesn't."""
    if not os.path.exists(directory):
        os.makedirs(directory)


def main():
    """Main function to orchestrate fetching and saving chat messages."""

    load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY")  # Ensure you have this in your .env file

    if not api_key:
        print("Error: YOUTUBE_API_KEY not found in .env file.")
        exit()

    args = setup_args()

    youtube_chat = YouTubeLiveChat(api_key)

    if args.channel_id:
        youtube_chat.set_channel_id(args.channel_id)
        print(f"Using channel ID from command line: {args.channel_id}")
    else:
        channel_id = youtube_chat.find_channel_id_by_name(args.channel_name)
        if not channel_id:
            print("Could not find channel ID from channel name. Exiting.")
            exit()
        youtube_chat.set_channel_id(channel_id)
        print(f"Using channel ID found from channel name: {channel_id}")

    live_video_id = youtube_chat.get_live_video_id()

    if live_video_id:
        print(f"Live video ID: {live_video_id}")
        active_live_chat_id = youtube_chat.get_active_live_chat_id(live_video_id)
        if active_live_chat_id:
            print(f"Active live chat ID: {active_live_chat_id}")

            # Determine filename
            ensure_data_directory_exists()  # Ensure the data directory exists
            filename = os.path.join("data", get_filename(youtube_chat))  # Prepend 'data' directory
            print("Streaming to ", filename)

            # CSV Headers
            csv_headers = ["author", "displayMessage", "publishedAt"]

            print("Polling for new messages and saving to CSV...")
            youtube_chat.poll_live_chat(active_live_chat_id, save_messages, filename, csv_headers)

            print(f"Polling complete and CSV should be saving now.")

        else:
            print("No active live chat found for this video.")
    else:
        print("No live events found for this channel.")


if __name__ == "__main__":
    main()