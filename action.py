import schedule
import time
import random
from mira_sdk import MiraClient, Flow, ComposioConfig
from dotenv import load_dotenv
import os
from tavily import TavilyClient

# Load environment variables
load_dotenv()

# API Keys
mira_api_key = os.getenv("MIRA_API_KEY")
composio_api_key = os.getenv("COMPOSIO_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

# Initialize Mira client
client = MiraClient(config={"API_KEY": mira_api_key})

# Initialize Tavily client
tclient = TavilyClient(api_key=tavily_api_key)

def fetch_and_post_news():
    news = tclient.search(
        "Give me top recent Indian news and provide a good enough description along with a specific link to the article.",
        max_results=2
    )["results"]
    
    # Define Flow
    version = "0.0.2"
    flow_name = f"@ansuman30/post-generator/{version}" if version else "@ansuman30/post-generator"

    # Prepare input data properly
    input_data = {
        "topic": f"Make a tweet about this news: {news} and also mention the source url in tweet"
    }

    response = client.flow.execute(
        flow_name,
        input_data,
        ComposioConfig(
            COMPOSIO_API_KEY=composio_api_key,
            ACTION="TWITTER_CREATION_OF_A_POST",  # Enum e.g., "TWITTER_POST", "DISCORD_SEND"
            TASK="Describe your task in natural language - {content}",  # {content} gets replaced with flow output
            ENTITY_ID="default"  # Platform-specific identifier
        )
    )
    print("Posted news successfully!")

# Schedule the job every 3 minutes
schedule.every(3).minutes.do(fetch_and_post_news)

# Run the scheduled job
while True:
    schedule.run_pending()
    time.sleep(1)
