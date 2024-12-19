import os
import requests
from dotenv import load_dotenv
import logging
from jose.exceptions import JWSError
from botocore.exceptions import NoCredentialsError, ClientError
from dating_plan_ai_agents.objects.utils import get_secret

logger = logging.getLogger(__name__)


class LLM:
    def __init__(self):
        load_dotenv()
        self.model_url = "https://api.openai.com/v1/chat/completions"
        try:
            secret = get_secret("my-app/config")
            self.api_key = secret["API_KEY"]
            print(f"Got secret from AWS secrets: {self.api_key}")
        except (NoCredentialsError, ValueError, KeyError, ClientError, JWSError) as exp:
            self.api_key = os.getenv("API_KEY")
            print(f"Failed to get secret: {exp}, using default values")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        self.max_tokens = 3000

    def get_llm_response(self, prompt):
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": self.max_tokens,
        }

        llm_response = ""
        response = requests.post(
            self.model_url, headers=self.headers, json=data, timeout=50
        )
        if response.status_code == 200:
            llm_response = response.json()["choices"][0]["message"]["content"]
            logger.info(f"LLM response: {llm_response}\n\n\n")
        else:
            print("Error:", response.status_code, response.text)

        return llm_response
