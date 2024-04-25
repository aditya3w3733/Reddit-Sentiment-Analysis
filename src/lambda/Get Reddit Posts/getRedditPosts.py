import json
import pymysql
from datetime import datetime, timedelta

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def time_since(dt):
    now = datetime.now()
    diff = now - dt
    if diff.days > 0:
        return f"{diff.days} day ago"
    else:
        hours = diff.seconds // 3600
        if hours > 1:
            return f"{hours} hours ago"
        elif hours == 1:
            return "1 hour ago"
        else:
            minutes = diff.seconds // 60
            if minutes > 1:
                return f"{minutes} minutes ago"
            else:
                return "Just now"

def lambda_handler(event, context):
    # connection to RDS instance
    connection = pymysql.connect(host='your-rds-instance-endpoint',
                                 user='username',
                                 password='password',
                                 db='rds-instance-name',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    response_data = []

    try:
        with connection.cursor() as cursor:
            # return distinct flairs
            cursor.execute("SELECT DISTINCT post_flair FROM posts WHERE post_flair IS NOT NULL")
            flairs = [row['post_flair'] for row in cursor.fetchall()]

            #last 24 hours or 3 days
            query = "SELECT * FROM posts WHERE post_creation_date > NOW() - INTERVAL 3 DAY"
            cursor.execute(query)
            results = cursor.fetchall()


            response_data = []

            for row in results:
                post_creation_date = row["post_creation_date"] if isinstance(row["post_creation_date"], datetime) else datetime.strptime(row["post_creation_date"], DATE_FORMAT)
                time_ago = time_since(post_creation_date)

                card_data = {
                    "post_id": row["post_id"],
                    "post_title": row["post_title"],
                    "article_summary": row["article_summary"],
                    "comment_summary": row.get("comment_summary", "Comments not available"),
                    "news_link": row["news_link"],
                    "comments_link": f"https://www.reddit.com/{row['post_id']}",
                    "post_creation_date": time_ago,
                    "flair": row["post_flair"]
                }
                response_data.append(card_data)

        return {
            'statusCode': 200,
            'body': json.dumps({"posts": response_data, "flairs": flairs}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    finally:
        connection.close()
