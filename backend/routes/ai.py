from fastapi import APIRouter
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load env
load_dotenv()

router = APIRouter()

class TextInput(BaseModel):
    content: str

# API KEY
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY missing in .env")

client = OpenAI(api_key=OPENAI_API_KEY)


# ------------------ GPT CALL ------------------

def call_gpt(prompt):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a STRICT text editor. "
                        "You ONLY fix grammar and spelling. "
                        "You NEVER add content. "
                        "You NEVER change structure. "
                        "You NEVER merge lines. "
                        "You preserve formatting EXACTLY."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=300
        )

        output = res.choices[0].message.content.strip()

        # Fix Mac symbols
        output = output.replace("⌘", "Ctrl")

        return output

    except Exception as e:
        print("❌ GPT ERROR:", str(e))
        return None


# ------------------ SAFETY FILTER ------------------

def preserve_structure(original, improved):
    # If model destroys line structure → fallback
    if len(improved.split("\n")) < len(original.split("\n")) * 0.7:
        return original

    # If model adds too much content → fallback
    if len(improved) > len(original) * 1.4:
        return original

    return improved


# ------------------ SUMMARIZE ------------------

@router.post("/summarize")
def summarize(data: TextInput):
    text = data.content.strip()

    prompt = f"""
Summarize the following notes.

Rules:
- Keep key points only
- Keep definitions unchanged
- Keep formulas unchanged
- Do NOT add new information
- Keep it short
- Maintain formatting

Text:
{text}
"""

    output = call_gpt(prompt)

    if not output:
        return {"summary": "⚠️ Failed to generate summary"}

    return {"summary": output}


# ------------------ IMPROVE ------------------

@router.post("/improve")
def improve(data: TextInput):
    text = data.content.strip()

    prompt = f"""
You are a strict text editor.

Your job:
Fix grammar ONLY.

STRICT RULES:
- Do NOT add ANY new content
- Do NOT add ANY new headings or sections
- Do NOT complete or expand sentences
- Do NOT generate examples
- Do NOT add anything that is not in the original text
- Keep EXACT same number of lines
- Keep EXACT same structure
- Keep EXACT same bullets and headings
- Only fix grammar and spelling

Return ONLY corrected version of SAME text.

Text:
{text}
"""

    output = call_gpt(prompt)

    if not output:
        return {"improved": "⚠️ Failed to improve text"}

    # 🔥 HARD FILTER: remove extra added content
    original_lines = text.split("\n")
    improved_lines = output.split("\n")

    # Keep only same number of lines
    improved_lines = improved_lines[:len(original_lines)]

    # Rebuild text
    output = "\n".join(improved_lines)

    return {"improved": output}