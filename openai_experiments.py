import openai
import argparse
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file",
        help="Text file to use as input for AI cataloging",
        required=True,
    )
    parser.add_argument(
        "-m",
        "--model",
        help="OpenAI model to use",
        required=True,
    )
    args = parser.parse_args()
    model = args.model
    file = args.file
    text = Path(file).read_text()
    base_prompt = """Provide a list of named people, places, other entities, and relationships between 
    them that are seen in the text below. This text was produced using OCR software on a scanned piece 
    of campaign literature related to an election in the United States in 1996. Use neutral, academic, 
    and accurate language."""
    full_prompt = f"{base_prompt}\n\n{text}"

    openai.api_key = os.getenv("OPENAI_API_KEY")

    if model == "gpt-3.5-turbo":
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": full_prompt},
            ],
        )
        print(response)


if __name__ == "__main__":
    main()
