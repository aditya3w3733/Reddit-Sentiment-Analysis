import praw
import csv
import re  # Import the regular expressions library
import pandas as pd

reddit = praw.Reddit(
    client_id="OrRHVzQoWjcebF3mcuethQ",
    client_secret="1vw76CcfiiKqYqSHdp7CbBwvn1TBng",
    user_agent="app-film"
)

def get_news_link(post_id):
    try:
        submission = reddit.submission(id=post_id)

        # Priority 1: Check if the submission URL itself is the news link
        if not submission.is_self:  # Check if it's not a self-post (text post)
            #print(f"Submission URL: FOR POST ID {post_id} : {submission.url}")
            return submission.url

        # Priority 2: If it's a self-post, search for potential links in the text
        link_pattern = r'https?://\S+'
        potential_links = re.findall(link_pattern, submission.selftext)
        if potential_links:
            print(f"Link retrieved for post ID {post_id}: {potential_links}")
            return potential_links[0]

        # Fallback
        return None  # No suitable link found

    except Exception as e:
        print(f"Error retrieving news link for post {post_id}: {e}")
        return None

# Load post IDs from post_ids.csv
post_ids_df = pd.read_csv('post_ids.csv')

# Add a new column for news links
post_ids_df['news_link'] = post_ids_df['post_id'].apply(get_news_link)

# Save the updated DataFrame to post_ids.csv
post_ids_df.to_csv('post_ids.csv', index=False)

print(post_ids_df)
