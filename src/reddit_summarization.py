import praw
import pandas as pd
import requests
import openai
from bs4 import BeautifulSoup
import mysql.connector
import time

openai.api_key = "your-openai-api-key"

# Your Reddit API credentials
reddit = praw.Reddit(
    client_id="your-credentials",
    client_secret="your-credentials",
    user_agent="your-credentials"
)

# Function to fetch article text from URL
def fetch_article_text(article_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
    try:
        response = requests.get(article_url, headers=headers)
        response.raise_for_status()
        article_text = response.text
        return response.text
    except Exception as e:
        print(f"Error fetching article: {e}")
        return None

# Function to extract text chunks from HTML content
def extract_text_chunks(html_content, chunk_size=4000):
    soup = BeautifulSoup(html_content, 'html.parser')
    text_elements = soup.find_all('p') or soup.find_all('div')

    chunks = []
    current_chunk = ""
    for element in text_elements:
        text = element.get_text()
        if len(current_chunk) + len(text) > chunk_size:
            chunks.append(current_chunk)
            current_chunk = ""
        current_chunk += text

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

# Function to summarize text using OpenAI's ChatGPT
def summarize_with_chatgpt(article_chunks):
    summary_pieces = []
    for chunk in article_chunks:
        prompt = f"Summarize the following news article in 3-4 clear and concise sentences without repetition:\n {chunk}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        summary_piece = response['choices'][0]['message']['content'].strip()
        summary_pieces.append(summary_piece)
        time.sleep(20)  # Sleep for 20 seconds between OpenAI requests

    full_summary = ". ".join(summary_pieces)
    return full_summary

# Function to summarize text with sentiment analysis
def summarize_with_sentiment(post_summary, comments):
    comment_prompts = []
    for comment in comments:
        comment_prompts.append(f"* **Comment:** {comment} (Sentiment: Analyze sentiment here)")  # Adjusted to handle truncated comments

    full_prompt = f"""**Post Summary:** {post_summary}

{''.join(comment_prompts)}

**Summarize the comments above, including their sentiment towards the post (positive, negative, or neutral).**"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": full_prompt}]
    )
    summary = response['choices'][0]['message']['content'].strip()
    time.sleep(20)
    return summary


# Function to fetch post IDs and news links from the database
def fetch_post_data_from_database():
    conn = mysql.connector.connect(
        database="reddit_summary",  # Database name updated
        user="aditya3w3733",
        password="aditya3w3733",
        host="redditsummarization.c16wsgw4u3b2.ap-south-1.rds.amazonaws.com",
        port="3306"
    )

    cursor = conn.cursor()

    sql_query = "SELECT post_id, news_link FROM posts"
    cursor.execute(sql_query)
    post_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return post_data

# Function to fetch comments for a post from the database
def fetch_comments_from_database(post_id, max_comment_length=500, max_comments=15):
    conn = mysql.connector.connect(
        database="reddit_summary",
        user="aditya3w3733",
        password="aditya3w3733",
        host="redditsummarization.c16wsgw4u3b2.ap-south-1.rds.amazonaws.com",
        port="3306"
    )
    cursor = conn.cursor(dictionary=True)

    sql_query = f"SELECT comment FROM comments WHERE post_id = '{post_id}' LIMIT {max_comments}"
    cursor.execute(sql_query)
    comments = cursor.fetchall()

    truncated_comments = []
    for comment in comments:
        truncated_comment = comment['comment'][:max_comment_length]  # Truncate comment to maximum length
        truncated_comments.append(truncated_comment)

    cursor.close()
    conn.close()

    return truncated_comments




# Function to update post summaries in the database
def update_post_summary_in_database(post_id, article_summary, comment_summary):
    conn = mysql.connector.connect(
        database="reddit_summary",
        user="aditya3w3733",
        password="aditya3w3733",
        host="your-rds-instance-endpoint",
        port="3306"
    )
    cursor = conn.cursor()

    sql_query = "UPDATE posts SET article_summary = %s, comment_summary = %s WHERE post_id = %s"
    cursor.execute(sql_query, (article_summary, comment_summary, post_id))
    conn.commit()

    cursor.close()
    conn.close()


# Main logic
post_data_from_database = fetch_post_data_from_database()

for post_id, news_link in post_data_from_database:
    article_text = fetch_article_text(news_link)
    if article_text is not None:
        article_chunks = extract_text_chunks(article_text)
        article_summary = summarize_with_chatgpt(article_chunks)

        comments = fetch_comments_from_database(post_id)

        comment_summary = summarize_with_sentiment(article_summary, comments)

        update_post_summary_in_database(post_id, article_summary, comment_summary)

        print(f"\n--- Summary for Post ID: {post_id} ---")
        print(f"Article Summary: {article_summary}")
        print(f"Comment Summary: {comment_summary}")
    else:
        print("Error fetching article. Skipping summarization")
