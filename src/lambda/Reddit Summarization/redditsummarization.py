import praw
import pandas as pd
import requests
import openai # ==0.28 version
from bs4 import BeautifulSoup
import mysql.connector
import time

openai.api_key = "your-openai-api-key"

reddit = praw.Reddit(
    client_id="your-praw-creds",
    client_secret="your-praw-creds",
    user_agent="your-praw-creds"
)


def lambda_handler(event, context):
    with get_db_connection() as conn:
        if not delete_previous_posts(conn):
            print("No posts to delete or deletion failed!")
        process_summaries(conn)
    return {
        'statusCode': 200,
        'body': 'Summarization completed successfully.'
    }


def get_db_connection():
    return mysql.connector.connect(
        database="your-instance",  
        user="instance-username",
        password="instance-password",
        host="your-rds-endpoint",
        port="port-no"
    )


def delete_previous_posts(conn):
    try:
        with conn.cursor() as cursor:
            # Check if there are posts to delete
            cursor.execute("SELECT COUNT(*) FROM posts")
            if cursor.fetchone()[0] <= 12:
                return False  # No posts to delete
            
            # Multi-statement execution requires enabling multi=True
            query = """
                DELETE c FROM comments c
                JOIN (SELECT post_id FROM posts ORDER BY post_id ASC LIMIT 6) AS p
                ON c.post_id = p.post_id;
                DELETE FROM posts
                ORDER BY post_id ASC
                LIMIT 6;
            """
            for result in cursor.execute(query, multi=True):
                pass
            conn.commit()
        return True
    except Exception as e:
        print(f"Failed to delete old posts and comments: {e}")
        conn.rollback()
        return False


def process_summaries(conn):
    posts = fetch_post_data_from_database(conn)
    for post_id, post_title, news_link in posts:
        article_text = fetch_article_text(news_link)
        if article_text:
            article_chunks = extract_text_chunks(article_text)
            article_summary = summarize_with_chatgpt(article_chunks, post_title)
            comments = fetch_comments_from_database(post_id, conn)
            comment_summary = summarize_with_sentiment(article_summary, comments)
            update_post_summary_in_database(post_id, article_summary, comment_summary, conn)

            print(f"\n--- Summary for Post ID: {post_id} ---")
            print(f"Article Summary: {article_summary}")
            print(f"Comment Summary: {comment_summary}")
        else:
            print(f"Error fetching article for Post ID: {post_id}. Skipping summarization.")



def fetch_article_text(article_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',  # Do Not Track Request Header
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    try:
        response = requests.get(article_url, headers=headers)
        response.raise_for_status()  # will raise an HTTPError for bad responses
        return response.text
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error for URL {article_url}: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request Exception for URL {article_url}: {e}")
    return None


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


# gpt3.5- tubro summarization
def summarize_with_chatgpt(article_chunks, post_title):
    chunk_summaries = []
    for chunk in article_chunks:
        max_retries = 3
        retries = 0
        
        while retries < max_retries:
            try:
                prompt = f"Summarize this section of the article titled '{post_title}' in a few concise sentences without repetition, ensuring that the context of the entire article is considered:\n\n{chunk}"
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                summary_piece = response['choices'][0]['message']['content'].strip()
                chunk_summaries.append(summary_piece)
                time.sleep(25)  
                break  # break if successful
            except openai.error.RateLimitError:
                retries += 1
                print("Rate limit exceeded. Waiting 60 seconds before retrying...")
                time.sleep(60)  # wait for 60 seconds before retrying
            except openai.error.OpenAIError as e:
                print(f"An OpenAI API error occurred: {str(e)}")
                return None  # Return None if an error occurs
        
        if retries == max_retries:
            print("Max retries reached for chunk summarization. Failed to summarize")
            return None 

    # compile the individual summaries into one
    combined_summary = " ".join(chunk_summaries)
    
    final_summary_prompt = f"Based on the following summaries, provide a concise and comprehensive summary for the article without repetition:\n\n{combined_summary}"
    try:
        final_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": final_summary_prompt}]
        )
        full_summary = final_response['choices'][0]['message']['content'].strip()
        return full_summary
    except openai.error.OpenAIError as e:
        print(f"Failed to generate final summary: {str(e)}")
        return None



def summarize_with_sentiment(post_summary, comments):
    comment_prompts = [f"* **Comment:** {comment}" for comment in comments]
    full_prompt = f"**Article Summary:** {post_summary}\n\n**Comments:**\n" + "\n".join(comment_prompts) + "\nSummarize the comments considering their sentiment (positive, negative, neutral)."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": full_prompt}]
        )
        summary = response['choices'][0]['message']['content'].strip()
        return summary
    except openai.error.OpenAIError as e:
        print(f"Failed to summarize comments: {e}")
        return None


def fetch_post_data_from_database(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT post_id, post_title, news_link FROM posts")
        return cursor.fetchall()


def fetch_comments_from_database(post_id, conn, max_comments=15):
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT comment FROM comments WHERE post_id = %s LIMIT %s", (post_id, max_comments))
        return [comment['comment'] for comment in cursor.fetchall()]



def update_post_summary_in_database(post_id, article_summary, comment_summary, conn):
    with conn.cursor() as cursor:
        cursor.execute("UPDATE posts SET article_summary = %s, comment_summary = %s WHERE post_id = %s", (article_summary, comment_summary, post_id))
        conn.commit()

