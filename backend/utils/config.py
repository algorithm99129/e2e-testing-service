import os
from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")


config = Config()
