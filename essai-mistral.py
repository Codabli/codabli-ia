import os
from mistralai.client import Mistral
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
api_key = os.environ["MIS_AI_ENDPOINT_API_KEY"]

client = Mistral(api_key=api_key)
SYSTEM = Path("prompts/PROMPT.md").read_text(encoding="utf-8")

stream = client.chat.stream(
    model="mistral-small-latest",  # ou "mistral-large-latest"
    messages=[
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": "gouzi gouzi ,c'est possible pour un compte dansé ?"},
    ],
    temperature=0.3,
)

# 2. Boucler sur le flux pour afficher le résultat au fur et à mesure
for chunk in stream:
    delta_content = chunk.data.choices[0].delta.content
    if delta_content is not None:
        print(delta_content, end="", flush=True)
print() # Saut de ligne final