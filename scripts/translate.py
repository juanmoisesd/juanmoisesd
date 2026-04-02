import os
from openai import OpenAI

client = OpenAI()

with open("templates/README.base.md", "r", encoding="utf-8") as f:
    text = f.read()

response = client.chat.completions.create(
    model="gpt-5",
    messages=[
        {"role": "user", "content": f"Translate to Spanish:\n\n{text}"}
    ]
)

translated = response.choices[0].message.content

os.makedirs("generated", exist_ok=True)

with open("generated/README.es.md", "w", encoding="utf-8") as f:
    f.write(translated)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(text)

print("OK")
