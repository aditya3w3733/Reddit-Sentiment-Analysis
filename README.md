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
- **Boto3**: AWS SDK for Python, used for interacting with AWS services programmatically.

## Workflow
1. **Scraping**: Every 24 hours, triggered by Amazon EventBridge, the scraping Lambda function(redditscraper) activates. It uses PRAW to fetch the latest technology posts from Reddit and BeautifulSoup to extract relevant content from the linked articles.
   
2. **Summarization**: The extracted content is then passed to another Lambda function(redditsummarization) where GPT-3.5 Turbo is used to generate concise summaries. This step involves cleaning and chunking the text due to token limitations and ensuring that summaries remain relevant and coherent.

3. **Data Management**: Summarized data is stored in an AWS RDS MySQL database, which maintains records of posts, articles, and comment summaries. This allows efficient retrieval and management of content.

4. **API Endpoint**: A Lambda function(getRedditPosts) acts as an API endpoint, interfaced through API Gateway. This function queries the RDS instance and returns the latest summaries in a structured JSON format.

5. **Frontend**: The frontend, hosted on AWS S3, uses JavaScript to call the API endpoint and display the summaries. The site is updated daily to reflect the most recent digests.

6. **Hosting and Deployment**: The entire frontend is statically hosted on S3, providing high availability and scalability. The backend Lambda functions are stateless and serverless, allowing them to handle varying loads effectively.


## System Architecture 

![image](https://github.com/aditya3w3733/TechDigest/assets/104208359/6c25313b-dedb-4675-a03f-f15aa8593ae3)



---



Original Reddit Post: www.reddit.com/1cbez15

Article Link: https://techcrunch.com/2024/04/23/tesla-profits-drop-55-company-says-ev-sales-under-pressure-from-hybrids/

Article Title : Tesla profits drop 55%, company says EV sales 'under pressure' from hybrids

### Article Summary: 

Tesla reported a 55% decrease in profits in the first quarter, attributing it to reduced sales of electric vehicles influenced by competition from hybrid vehicles. Despite this setback, the company remains committed to advancing technology through the development of more affordable models and enhancing autonomy using AI. Tesla also experienced growth in energy storage and services, with future plans including the launch of a robotaxi service and a delay in production of the Tesla Semi until late 2025.

### Comment Summary: 

The comments overall express a negative sentiment towards Tesla, with criticism directed at Elon Musk, the company's CEO, as well as concerns about the quality of Tesla's products and the company's future prospects. Many commenters feel disillusioned with the brand and question its ability to compete with other car manufacturers in the long run. There is skepticism about Tesla's promises and a sense of disappointment among consumers.

---
## Recent Updates

- Implemented sub-categories (flairs) to organize content by specific topics within technology news, enhancing user navigation and content discovery.
  
---
## Future Work

- Improvements to the summarization algorithm to better handle the context window limitation of OpenAI's API.
  
