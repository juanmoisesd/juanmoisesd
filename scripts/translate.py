import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

with open("templates/README.base.md", "r", encoding="utf-8") as f:
    text = f.read()

response = client.responses.create(
    model="gpt-4.1-mini",
    input=f"Translate to Spanish:\n\n{text}"
)

translated = response.output_text

os.makedirs("generated", exist_ok=True)

with open("generated/README.es.md", "w", encoding="utf-8") as f:
    f.write(translated)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(text)

print("DONE")
