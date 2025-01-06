import praw
import os

# I dont think reddit is a good data source at the moment, I would take some entries from a subreddit selectively
def get_submission_details(url: str) -> str:
    """
    Given a Reddit post URL, this function uses PRAW to fetch the submission
    and return a string containing basic info plus the top 20 comments.
    """
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    # Initialize Reddit instance
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent="example_application/0.1 by YOUR_USERNAME"
    )

    # Retrieve the submission from the URL
    submission = reddit.submission(url=url)

    # Build a list to store lines of text
    output_lines = []

    # Add basic info to output
    output_lines.append(f"Title: {submission.title}")
    output_lines.append(f"Author: {submission.author}")
    output_lines.append(f"Subreddit: r/{submission.subreddit}")
    output_lines.append(f"Score: {submission.score}")
    output_lines.append(f"Number of comments: {submission.num_comments}")
    output_lines.append(f"URL: {submission.url}")
    output_lines.append(f"Selftext: {submission.selftext or 'No selftext available.'}")

    # Get top-level comments
    submission.comments.replace_more(limit=0)
    top_comments = submission.comments[:20]
    
    # Append top 20 comments (or fewer if there aren't 20)
    for i, comment in enumerate(top_comments, start=1):
        # Truncate the comment body for readability or remove truncation if you want full text
        truncated_body = (comment.body[:200] + "...") if len(comment.body) > 200 else comment.body
        output_lines.append(f"\nTop-level comment #{i}: {truncated_body}")

    # Join all the lines into one string
    return "\n".join(output_lines)