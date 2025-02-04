from fastapi import APIRouter, HTTPException
from memeai.twitter.config import settings
from memeai.twitter.client import client
from memeai.agents.init_agent import init_agent
import json
import logging
import os

# Set the API key as an environment variable
os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY

# Initialize the router and logger
router = APIRouter(prefix="/letta_agent", tags=["letta_agent"])
logger = logging.getLogger(__name__)

os.environ["AGENT_ID"] = init_agent()
AGENT_ID = os.environ["AGENT_ID"]


async def generate_tweet_content(message: str) -> str:
    """
    Generate a tweet using the Letta agent.

    Args:
        message (str): The input message to generate a tweet from.

    Returns:
        str: The generated tweet content.

    Raises:
        Exception: If an error occurs during the generation process.
    """
    environment = "Twitter"
    try:
        logger.info(f"Generating tweet for message: {message}")
   
        # Send the message to the Letta agent
        response = client.send_message(
            agent_id=AGENT_ID, message=f"[system] Explore {environment} environment, call functions to explore the environment and make actions.", role="system"
        )

        # Parse the response
        response_data = response.messages[1].function_call.arguments
        parsed_response = json.loads(response_data)

        # Extract the generated message
        generated_message = parsed_response.get("message")
        if not generated_message:
            raise ValueError("Generated message is missing from the response.")
     
        return generated_message

    except Exception as e:
        logger.exception(f"Error in generate_tweet_content: {str(e)}")
        raise


# Endpoint using the utility function
@router.post("/generate")
async def generate_tweet(message: str):
    try:
        generated_message = await generate_tweet_content(message)
        return {"message": generated_message}
    except ValueError as e:
        logger.error(f"ValueError: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid response: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to generate tweet: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while generating the tweet. Please try again later.",
        )
