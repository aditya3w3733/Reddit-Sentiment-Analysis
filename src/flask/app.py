from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

# Connect to MySQL database
conn = mysql.connector.connect(
    host="redditsummarization.c16wsgw4u3b2.ap-south-1.rds.amazonaws.com",
    user="aditya3w3733",
    password="aditya3w3733",
    database="reddit_summary"
)

# Define route to fetch data for each post
@app.route('/posts', methods=['GET'])
def get_posts():
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT post_id, post_title, article_summary, news_link FROM posts")
    posts_data = cursor.fetchall()
    cursor.close()

    posts = []
    for post in posts_data:
        post_id = post['post_id']
        post_title = post['post_title']
        article_summary = post['article_summary']
        news_link = post['news_link']
        reddit_link = f"https://www.reddit.com/{post_id}"

        # Construct the card format
        card = {
            "post_title": post_title,
            "article_summary": article_summary,
            "comment_summary": "",  # Initialize to empty string for now
            "news_link": news_link,
            "reddit_link": reddit_link
        }
        posts.append(card)

    return jsonify(posts)

if __name__ == '__main__':
    app.run(debug=True)
