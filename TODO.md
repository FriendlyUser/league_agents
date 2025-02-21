BUILD A LANGCHAIN APP THAT USES THE YOUTUBE_TRANSCRIPT_API pulls the transcript feeds the team data into it, and contains the list of champions and players to autocorrect. As a follow up chain, also at the same time clean statements like Let me know if you'd like a more detailed look at any specific aspects!, automatically save to file.

Use autogen in python, we want to pull data from the csv for each team, should be able to group by game, stat line, etc ....

And the entire youtube transcripts summary of the team strengths and weaknesses to determine if odds are fair, we will have multiple analyis,

The first is to judge a given matchup between two games and estimate the oods, the second is to automatically pull odds from an site to use as reference.


Given the following initial app

Act like an expert in legend of legends, we want to automatically generate video highlights from a given youtube transcripts.

Given the following transcript data, you must analyze it and return at most 3 minutes  long snippets with a start and end range. We want to have the end_time

Return an array of snippets, focus on first bloods, first towers, objective secures (dragons, rift herald, grubs, baron, attakan), large team fights and turning points in the game. Make sure the we start taking highlights when champion select (drafting begins)

Force it to return in srt format, reuse the existing youtube transcript to find the nearby entries from the start time + text, and then follow up with more requests, we can have one request to figure out how many games are available, and then when the games are ended and started, draft phrase timings, etc..., from there we isolate the highlights returned or send each game + draft individually, and automate the highlight video and then automatically upload (lots of competition already)
