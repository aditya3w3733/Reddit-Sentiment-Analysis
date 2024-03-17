import praw
import csv
import os
import time

reddit = praw.Reddit(
    client_id="your-reddit-api-creds",
    client_secret="your-reddit-api-creds",
    user_agent="your-reddit-api-creds"
)

subreddit = reddit.subreddit("technology")

flairs = [
    "Artificial Intelligence",
    "Biotechnology",
    "Business",
    "Crypto",
    "Energy",
    "Hardware",
    "Machine Learning",
    "Nanotech/Materials",
    "Networking/Telecom",
    "Net Neutrality",
    "Politics",
    "Privacy",
    "Robotics/Automation",
    "Security",
    "Social Media",
    "Society",
    "Software",
    "Space",
    "Transportation"
]

# Create the 'output' directory if it doesn't exist
output_directory = 'output'
os.makedirs(output_directory, exist_ok=True)

min_comment_score = 5  # Set the minimum comment score

for flair in flairs:
    # Replace slash with underscore in flair name for file creation
    flair_file_name = flair.replace("/", "_")

    top_posts = subreddit.search(f"flair:{flair}", sort="top", time_filter="all", limit=1000)

    # Write top-level comments with a minimum score of 10 to CSV
    with open(f"output/{flair_file_name}_comments.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["post_id", "comment_id", "comment"])
        for post in top_posts:
            submission = reddit.submission(id=post.id)
            #try:
                #submission.comments.replace_more(limit=None)
                #time.sleep(5)  # Ensure all comments are loaded
            #except praw.exceptions.PRAWException as e:
                #print(f"Error loading comments for post {post.id}: {e}")
                #continue  # Skip to the next post

            for comment in submission.comments:
                if isinstance(comment, praw.models.Comment) and comment.is_root:  # and comment.score >= min_comment_score:
                    writer.writerow([post.id, comment.id, comment.body])
