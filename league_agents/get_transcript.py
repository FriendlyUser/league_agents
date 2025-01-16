import json
from youtube_transcript_api import YouTubeTranscriptApi

video_id="aNUt1VfGd1I"
transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
transcript = transcript_list.find_generated_transcript(['en'])
transcript_data = transcript.fetch()
video_title = "BFX vs KT - T1 vs DK | 2025 LCK CUP Group Battle.json"
with open(f'data/vods/{video_title}.json', 'w') as f:
    json.dump(transcript_data, f)