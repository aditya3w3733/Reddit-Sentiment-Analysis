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
    # Setup the connection to RDS
    connection = pymysql.connect(host='your-rds-instance-endpoint',
                                 user='username',
                                 password='password',
                                 db='rds-instance-name',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    response_data = []

    try:
        with connection.cursor() as cursor:
            #last 24 hours
            query = "SELECT * FROM posts WHERE post_creation_date > NOW() - INTERVAL 3 DAY"
            cursor.execute(query)
            results = cursor.fetchall()

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
                    "post_creation_date": time_ago
                }
                response_data.append(card_data)

    finally:
        connection.close()

    return {
        'statusCode': 200,
        'body': json.dumps(response_data),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
