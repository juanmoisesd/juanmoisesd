import os
import json
import hashlib
import re
from openai import OpenAI

client = OpenAI()

# ======================
# CONFIG
# ======================

LANGUAGES = {
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "pl": "Polish",
    "nl": "Dutch",
    "ro": "Romanian",
    "cs": "Czech",
    "sk": "Slovak",
    "sl": "Slovenian",
    "hr": "Croatian",
    "hu": "Hungarian",
    "bg": "Bulgarian",
    "el": "Greek",
    "da": "Danish",
    "fi": "Finnish",
    "sv": "Swedish",
    "et": "Estonian",
    "lv": "Latvian",
    "lt": "Lithuanian",
    "mt": "Maltese",
    "ga": "Irish",
    "zh": "Chinese",
    "ar": "Arabic",
    "he": "Hebrew",
    "hi": "Hindi"
}

BASE_PATH = "templates/README.base.md"
OUTPUT_DIR = "generated"
MEMORY_PATH = "scripts/translation_memory.json"
STATE_PATH = "scripts/state.json"
GLOSSARY_PATH = "scripts/glossary.json"

DISCLAIMER = """\
> ⚠️ This document is automatically translated.
> The authoritative and citable version is the English original.
"""

# ======================
# LOAD FILES
# ======================

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

GLOSSARY = load_json(GLOSSARY_PATH)
MEMORY = load_json(MEMORY_PATH)

# ======================
# UTILS
# ======================

def compute_hash(text):
    return hashlib.md5(text.strip().lower().encode("utf-8")).hexdigest()

def split_sections(text):
    return text.split("\n\n")

def protect_code_blocks(text):
    code_blocks = re.findall(r"```.*?```", text, re.DOTALL)
    placeholders = {}

    for i, block in enumerate(code_blocks):
        key = f"__CODE_BLOCK_{i}__"
        placeholders[key] = block
        text = text.replace(block, key)

    return text, placeholders

def restore_code_blocks(text, placeholders):
    for key, block in placeholders.items():
        text = text.replace(key, block)
    return text

def apply_glossary(text, lang_code):
    for term, translations in GLOSSARY.items():
        if lang_code in translations:
            text = text.replace(term, translations[lang_code])
    return text

# ======================
# TRANSLATION CORE
# ======================

def translate_section(text, target_lang):
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {
                "role": "system",
                "content": """
You are a scientific translator.

Rules:
- Preserve scientific accuracy
- Do NOT translate code
- Keep formatting
- Maintain terminology consistency
- Do NOT add explanations
"""
            },
            {
                "role": "user",
                "content": f"Translate to {target_lang}:\n\n{text}"
            }
        ]
    )
    return response.choices[0].message.content

# ======================
# INCREMENTAL TRANSLATION
# ======================

def translate_incremental(sections, lang, code):
    results = []

    for section in sections:
        h = compute_hash(section)

        if h in MEMORY and code in MEMORY[h]["translations"]:
            results.append(MEMORY[h]["translations"][code])
            continue

        # proteger código
        protected, placeholders = protect_code_blocks(section)

        translated = translate_section(protected, lang)

        translated = restore_code_blocks(translated, placeholders)

        translated = apply_glossary(translated, code)

        # guardar memoria
        if h not in MEMORY:
            MEMORY[h] = {"original": section, "translations": {}}

        MEMORY[h]["translations"][code] = translated

        results.append(translated)

    return "\n\n".join(results)

# ======================
# STATE CONTROL
# ======================

def has_changed(text):
    new_hash = compute_hash(text)

    if not os.path.exists(STATE_PATH):
        return True, new_hash

    with open(STATE_PATH, "r") as f:
        state = json.load(f)

    return state.get("hash") != new_hash, new_hash

def save_state(hash_value):
    with open(STATE_PATH, "w") as f:
        json.dump({"hash": hash_value}, f)

def save_memory():
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(MEMORY, f, ensure_ascii=False, indent=2)

# ======================
# MAIN PIPELINE
# ======================

def main():
    if not os.path.exists(BASE_PATH):
        print("Base README not found")
        return

    with open(BASE_PATH, "r", encoding="utf-8") as f:
        base = f.read()

    changed, new_hash = has_changed(base)

    if not changed:
        print("No changes detected → skipping")
        return

    sections = split_sections(base)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for code, lang in LANGUAGES.items():
        print(f"Translating → {lang}")

        translated = translate_incremental(sections, lang, code)

        final_text = DISCLAIMER + "\n\n" + translated

        with open(f"{OUTPUT_DIR}/README.{code}.md", "w", encoding="utf-8") as f:
            f.write(final_text)

    # guardar inglés
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(base)

    save_memory()
    save_state(new_hash)

    print("Done.")

if __name__ == "__main__":
    main()