import openai, os
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()
api_key = os.environ["OVH_AI_ENDPOINT_API_KEY"]
SYSTEM = Path("prompts/PROMPT.md").read_text(encoding="utf-8")

client = openai.OpenAI(
    base_url="https://oai.endpoints.kepler.ai.cloud.ovh.net/v1",
    api_key = api_key,
    timeout=30.0,
    max_retries=0,
)

stream = client.chat.completions.create(
    model="Qwen3.5-9B",
    messages=[
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": "gouzi gouzi ,c'est possible pour un compte dansé ?"},
    ],
    temperature=0.3,
    stream=True,
)

for chunk in stream:
    d = chunk.choices[0].delta
    r = getattr(d, "reasoning", None)
    if r:
        print(f"\033[90m{r}\033[0m", end="", flush=True)
    if d.content:
        print(d.content, end="", flush=True)
print()