from openai import OpenAI
from dotenv import load_dotenv
import os

TEST_GENERATOR_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "generate_test_prompt.md")

load_dotenv()

client = OpenAI()

def generate_tests(terraform_code: str):
    with open(TEST_GENERATOR_PROMPT_PATH, "r") as f:
        prompt = f.read().format(terraform_code=terraform_code)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text