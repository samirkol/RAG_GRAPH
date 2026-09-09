from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI()


def create_embedding(text: str):
    """
    Create an embedding vector for a piece of text.
    """

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding