import praw
import mysql.connector
import pandas as pd
import re
import boto3 
import json
import datetime

reddit = praw.Reddit(
    client_id="your-praw-creds",
    client_secret="your-praw-creds",
    user_agent="your-praw-creds"
)


def get_news_link(post_id):
    try:
        submission = reddit.submission(id=post_id)

        if not submission.is_self:  # Check if it's not a self-post (text post)
            return submission.url

        link_pattern = r'https?://\S+'
        potential_links = re.findall(link_pattern, submission.selftext)
        if potential_links:
            return potential_links[0]
        return None

    except Exception as e:
        print(f"Error retrieving news link for post {post_id}: {e}")
        return None

def lambda_handler(event, context):
    # Run the main scraping function
    response = fetch_and_store_data(event, context)

    # if the main scraping lambda function completed successfully, invoke the summarization
    if response['statusCode'] == 200:
        invoke_summarization()
    
    # return the response from the redditscraper function
    return response

def fetch_and_store_data(event, context):
    conn = mysql.connector.connect(
        database="your-instance",  
        user="instance-username",
        password="instance-password",
        host="your-rds-endpoint",
        port="port-no"
    )

    subreddit = reddit.subreddit('technology')

    posts_data = []
    comments_data = []

    for submission in subreddit.top("day", limit=15):
        flair = submission.link_flair_text or 'General'
        comments = [comment for comment in submission.comments.list() if isinstance(comment, praw.models.Comment)]

        news_link = get_news_link(submission.id)
        creation_time = datetime.datetime.fromtimestamp(submission.created_utc)
        posts_data.append({
            "post_id": submission.id,
            "post_title": submission.title,
            "news_link": news_link,
            "post_flair": flair,
            "post_creation_date": creation_time.strftime('%Y-%m-%d %H:%M:%S'),
        })

        for comment in comments:
            comments_data.append({
                "comment_id": comment.id,
                "post_id": submission.id,
                "comment": comment.body
            })

    posts_df = pd.DataFrame(posts_data)
    comments_df = pd.DataFrame(comments_data)

    write_to_mysql(posts_df, comments_df, conn)

    conn.close()

    return {
        'statusCode': 200,
        'body': 'Data scraping and storing completed.'
    }

def write_to_mysql(posts_df, comments_df, conn):
    try:
        cursor = conn.cursor()

        for _, row in posts_df.iterrows():
            # Check if the post already exists
            cursor.execute("SELECT post_id FROM posts WHERE post_id = %s", (row['post_id'],))
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute("""
                    INSERT INTO posts (post_id, post_title, news_link, post_flair, post_creation_date)
                    VALUES (%s, %s, %s, %s, %s)
                """, (row['post_id'], row['post_title'], row['news_link'], row['post_flair'], row['post_creation_date']))
            else:
                print(f"Post {row['post_id']} already exists. Skipping insertion.")

        for _, row in comments_df.iterrows():
            cursor.execute("SELECT comment_id FROM comments WHERE comment_id = %s", (row['comment_id'],))
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute("""
                    INSERT INTO comments (comment_id, post_id, comment)
                    VALUES (%s, %s, %s)
                """, (row['comment_id'], row['post_id'], row['comment']))
            else:
                print(f"Comment {row['comment_id']} already exists. Skipping insertion.")

        conn.commit()
        print("Data successfully written to MySQL database.")

    except Exception as e:
        print(f"Error writing data to MySQL database: {e}")
        conn.rollback()

    finally:
        cursor.close()

def invoke_summarization():
    lambda_client = boto3.client('lambda')
    
    # invoke the reddit_summarization lambda function asynchronously
    try:
        invoke_response = lambda_client.invoke(
            FunctionName='redditsummarization',  # lambda fn name
            InvocationType='Event',  # async fn
            Payload=json.dumps({})  # pass any required payload for the fn
        )
        print(f"Invoked summarization function: {invoke_response}")
    except Exception as e:
        print(f"Error invoking summarization function: {e}")

