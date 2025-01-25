from mira_sdk import MiraClient, Flow, CompoundFlow, ComposioConfig
from mira_sdk.exceptions import FlowError
import json
import schedule
import time
from dotenv import load_dotenv
from tavily import TavilyClient
import os

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("MIRA_API_KEY")
composio_api_key = os.getenv("COMPOSIO_API_KEY")
tavily_api_key=os.getenv("TAVILY_API_KEY")

# Initialize Mira and Tavily clients
client = MiraClient(config={"API_KEY": api_key})
tclient = TavilyClient(api_key=tavily_api_key)

version = "0.1.0"
flow_name = f"@ansu/opiniontweetgenerator/{version}" if version else "@ansu/opiniontweetgenerator"

def fetch_and_store_news():
    """Fetches recent Indian news and creates a Google Doc using Composio"""
    try:
        # Fetch news
        news = tclient.search(
            "Give me top recent Indian news and provide a good enough description along with a specific link to the article.",
            max_results=2
        )["results"]

        input_dict = {"json_data": json.dumps(news)}

        # Execute Mira flow with ComposioConfig
        response = client.flow.execute(
                    flow_name,
                    input_dict,
                    ComposioConfig(
                        COMPOSIO_API_KEY=composio_api_key,
                        ACTION="TWITTER_CREATION_OF_A_POST",  # This is the Enum e.g., "TWITTER_POST", "DISCORD_SEND"
                        TASK="Describe your task in natural language - {content}",  # {content} is required and gets replaced with flow output
                        ENTITY_ID="default"  # Platform-specific identifier
                        )
        )

        print("Composio Response:", response)

    except FlowError as fe:
        print("Flow Execution Error:", fe)
    except Exception as e:
        print("Unexpected Error:", e)

# Schedule the function to run every 3 minutes
schedule.every(3).minutes.do(fetch_and_store_news)

print("Scheduler started! Fetching news every 3 minutes...")

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)  # Prevents high CPU usage
