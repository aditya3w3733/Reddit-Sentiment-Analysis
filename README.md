# TechDigest

TechDigest is an automated content aggregation and summarization platform that specifically targets technology-related news from Reddit. It delivers a daily digest of the top technology stories, providing concise summaries of articles and related discussions for tech enthusiasts who want to stay informed without investing a lot of time.

## Architecture
The system leverages a combination of AWS services, Python libraries, and the OpenAI API to scrape, process, summarize, and serve content.

### Components
- **AWS Lambda**: Runs the core functionality distributed across three functions:
  - `Data Collection`: Scrapes the top technology posts from Reddit.
  - `Data Summarization`: Summarizes the articles and comments.
  - `API Endpoint`: Serves the summarized content via API Gateway.
- **AWS RDS (MySQL)**: Stores and manages the scraped and processed data.
- **Amazon EventBridge**: Schedules the daily scraping and summarization tasks.
- **OpenAI GPT-3.5 Turbo**: Summarizes the content, capturing the essence of articles and sentimental summary of comments.
- **AWS S3**: Hosts the front-end website displaying the digested content.
- **API Gateway**: Provides RESTful API endpoints that interface with Lambda functions.
- **IAM Roles**: AWS IAM roles and policies are carefully defined to grant minimum necessary permissions to each service.

### Tools and Libraries
- **PRAW (Python Reddit API Wrapper)**: Enables interaction with the Reddit API for scraping posts and comments.
- **BeautifulSoup**: Parses HTML content from articles for text extraction.
- **Requests**: Facilitates HTTP requests to fetch articles.

## Workflow
1. **Scraping**: Every 24 hours, triggered by Amazon EventBridge, the scraping Lambda function(redditscraper) activates. It uses PRAW to fetch the latest technology posts from Reddit and BeautifulSoup to extract relevant content from the linked articles.
   
2. **Summarization**: The extracted content is then passed to another Lambda function(redditsummarization) where GPT-3.5 Turbo is used to generate concise summaries. This step involves cleaning and chunking the text due to token limitations and ensuring that summaries remain relevant and coherent.

3. **Data Management**: Summarized data is stored in an AWS RDS MySQL database, which maintains records of posts, articles, and comment summaries. This allows efficient retrieval and management of content.

4. **API Endpoint**: A Lambda function(getRedditPosts) acts as an API endpoint, interfaced through API Gateway. This function queries the RDS instance and returns the latest summaries in a structured JSON format.

5. **Frontend**: The frontend, hosted on AWS S3, uses JavaScript to call the API endpoint and display the summaries. The site is updated daily to reflect the most recent digests.

6. **Hosting and Deployment**: The entire frontend is statically hosted on S3, providing high availability and scalability. The backend Lambda functions are stateless and serverless, allowing them to handle varying loads effectively.





---



Summary for Reddit Post: www.reddit.com/1ba5xpl 

Article Link: https://www.bloomberg.com/news/articles/2024-03-08/biden-backs-measure-forcing-tiktok-sale-as-house-readies-vote

### Article Summary: 

President Joe Biden has expressed strong support for a House bill that would require TikTok's Chinese owners to sell the app. He stated that he would sign the bill if it passes, signaling his commitment to the proposal. This move comes amid ongoing concerns about national security and data privacy issues surrounding Chinese-owned technology companies operating in the United States. Biden made the comments before boarding Air Force One for a campaign event in Pennsylvania.

### Comment Summary: 

The comments express mixed sentiments towards the post. Some are supportive of the idea of requiring TikTok's Chinese owners to sell the app due to national security concerns, while others have reservations about potential unintended consequences or criticize the US government's actions. Overall, the sentiment is leaning more towards negative or critical viewpoints.


---
## Future Work

- Improvements to the summarization algorithm to better handle the context window limitation of OpenAI's API. 
- In the future, TechDigest aims to offer users the option to view summaries and digests for specific sub-categories within technology news such as Artificial Intelligence, Machine Learning, Space Exploration, Robotics, and Energy. This feature will enable users to tailor the content feed to their interests, ensuring a personalized experience.
