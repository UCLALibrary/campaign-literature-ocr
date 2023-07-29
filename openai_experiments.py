import json
import os
import sys
import numpy
import openai

from pprint import pprint


def main():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    ocr_file = sys.argv[1]

    # list_models()
    prompt = get_prompt(ocr_file)

    gpt1 = get_gpt_as_dict(prompt)
    print("\nGPT Response:")
    pprint(gpt1, width=132)

    davinci = get_davinci_as_dict(prompt)
    print("\nDavinci Response:")
    pprint(davinci, width=132)
    print("\n")

    for field in ["Title", "Description", "Subject"]:
        gpt_embedding = get_embedding(gpt1.get(field))
        dvc_embedding = get_embedding(davinci.get(field))
        similarity_score = numpy.dot(gpt_embedding, dvc_embedding)
        print(f"{field} similarity: {similarity_score}")


def get_prompt(ocr_file: str) -> str:
    with open(ocr_file) as f:
        ocr_text = f.read()
    prompt = (
        "The text below was produced using OCR on a scanned document. "
        "Provide a Dublin Core metadata record for the original document. "
        "At a minumum, include 'Title', 'Subject', and 'Description' fields. "
        "Include other Dublin Core fields if they can be determined accurately; "
        "otherwise, leave them out of the response. "
        "Be sure to use neutral, unbiased language for the 'Description' field. "
        "Use 'sentence case' for the 'Title' field. "
        "Return only Dublin Core fields, correctly formatted as JSON. "
        f"Additional context: the name of the source document is {ocr_file}.\n"
        f"The text from the document is enclosed in three single quotes below: '''{ocr_text}'''"
    )
    return prompt


def get_gpt_as_dict(prompt: str, temperature: float = 0.1, top_p: float = 0.3) -> dict:
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=temperature,
        top_p=top_p,
    )
    # print(gpt_completion1.usage)
    response = completion.choices[0].message.content
    return json.loads(response)


def get_davinci_as_dict(
    prompt: str, temperature: float = 0.1, top_p: float = 0.3
) -> dict:
    # davinci is a regular Completion, not ChatCompletion
    completion = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=3000,
        temperature=temperature,
        top_p=top_p,
    )
    # print(completion.usage)
    response = completion.choices[0].text
    # davinci usually returns Subject as a Python list;
    # convert to string for consistency with gpt.
    json_response = json.loads(response)
    response_subjects = json_response.get("Subject")
    if isinstance(response_subjects, list):
        subjects = ", ".join(response_subjects)
        json_response["Subject"] = subjects
    return json_response


def get_embedding(text: str, model: str = "text-embedding-ada-002") -> list:
    embedding = openai.Embedding.create(input=[text], model=model)
    return embedding["data"][0]["embedding"]


def list_models():
    models = openai.Model.list()
    # models[data] is a list of dictionaries
    model_ids = [model["id"] for model in models["data"]]
    pprint(sorted(model_ids))


if __name__ == "__main__":
    main()

# Links to Wikidata are almost always wrong, and varied in their wrongness;
# Wikipedia links seem to all be correct.

# Other prompts

# prompt = (
#     "Identify the people mentioned in the document below. "
#     "Provide the names of the human beings identified, "
#     "and 1-2 sentences of biographical information. "
#     "Provide information only for real human beings, not for organizations or for laws. "
#     "If no information is available for a person, do not include them in your response. "
#     "For each person, also provide a link to their primary Wikipedia page, "
#     "and the reason that Wikipedia link was selected. "
#     f"Additional context: the name of the source document is {ocr_file}.\n"
#     f"Here is the document: {ocr_text}"
# )

# prompt = (
#     "Identify the people, organizations, and laws mentioned in the document below. "
#     "Provide a complete list with the names of the identified people, organizations, and laws, "
#     "and a 1-2 sentence factual summary about each one. "
#     "For each person, organization, and law in your response, "
#     "you must also provide a link to its primary Wikipedia page. "
#     "If no other information is available for an entity, do not include it in your response. "
#     f"Additional context: the name of the source document is {ocr_file}.\n"
#     f"Here is the document: {ocr_text}"
# )
