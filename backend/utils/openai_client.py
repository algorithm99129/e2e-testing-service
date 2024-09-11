from openai import OpenAI
from utils.config import config

client = OpenAI(api_key=config.openai_api_key)


def generate_description(error_msg):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Generate brief description about the test error",
            },
            {
                "role": "user",
                "content": f"Here is the error message: {error_msg}",
            },
        ],
        model="gpt-3.5-turbo",
    )

    return chat_completion.choices[0].message.content
