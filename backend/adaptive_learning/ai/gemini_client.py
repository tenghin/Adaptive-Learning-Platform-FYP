import json
import os
import re
from urllib import error, request

from adaptive_learning.ai.prompt_config import QUIZ_QUESTION_COUNT
from adaptive_learning.ai.prompt_builder import build_quiz_prompt

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"

# DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-lite" - have more usage

def _strip_code_fences(text):
    cleaned_text = text.strip()
    if cleaned_text.startswith("```"):
        cleaned_text = re.sub(r"^```(?:json)?\s*", "", cleaned_text)
        cleaned_text = re.sub(r"\s*```$", "", cleaned_text)
    return cleaned_text.strip()


def parse_json_response(text):
    cleaned_text = _strip_code_fences(text)
    return json.loads(cleaned_text)


def _call_gemini_api(prompt):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None, "Gemini API key is not configured"

    model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip()
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )

    request_body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }

    http_request = request.Request(
        url,
        data=json.dumps(request_body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with request.urlopen(http_request, timeout=30) as http_response:
            response_payload = json.loads(
                http_response.read().decode("utf-8")
            )
    except error.HTTPError as exc:
        return None, f"Gemini API request failed with status {exc.code}"
    except error.URLError:
        return None, "Gemini API request could not be completed"

    candidates = response_payload.get("candidates", [])
    if not candidates:
        return None, "Gemini API returned no candidates"

    content = candidates[0].get("content", {})
    parts = content.get("parts", [])
    if not parts:
        return None, "Gemini API returned an empty response"

    return parts[0].get("text", ""), None


def _fallback_summary(lesson_title, lesson_content):
    content = lesson_content.strip()
    first_sentence = content.split(".")[0].strip()
    summary = first_sentence or f"This lesson covers {lesson_title.lower()}."
    return {"summary": summary}


def _fallback_knowledge_graph(lesson_title, lesson_content):
    raw_lines = [line.strip() for line in lesson_content.splitlines() if line.strip()]
    concept_labels = []
    for line in raw_lines[:5]:
        cleaned_line = re.sub(r"^[#\-*\d.\s]+", "", line).strip()
        if cleaned_line:
            concept_labels.append(cleaned_line[:80])

    if not concept_labels:
        concept_labels = [lesson_title]

    concepts = []
    relationships = []
    for index, label in enumerate(concept_labels, start=1):
        concept_id = f"concept-{index}"
        concepts.append(
            {
                "id": concept_id,
                "label": label,
                "description": None,
            }
        )
        if index > 1:
            relationships.append(
                {
                    "source": f"concept-{index - 1}",
                    "target": concept_id,
                    "type": "related_to",
                }
            )

    return {
        "lesson_title": lesson_title,
        "concepts": concepts,
        "relationships": relationships,
    }

def generate_json(prompt, fallback_payload_factory):
    raw_text, error_message = _call_gemini_api(prompt)

    if error_message:
        return fallback_payload_factory(), error_message

    try:
        parsed = parse_json_response(raw_text)
        print("PARSED JSON:")
        print(parsed)
        return parsed, None
    except json.JSONDecodeError as e:
        print(e)
        return fallback_payload_factory(), "Gemini returned invalid JSON"


def generate_summary_payload(prompt, fallback_payload_factory):
    return generate_json(
        prompt,
        fallback_payload_factory
    )


def generate_knowledge_graph_payload(prompt, fallback_payload_factory):
    return generate_json(
        prompt,
        fallback_payload_factory
    )

def _fallback_quiz(lesson_title):
    return {
        "title": f"{lesson_title} Quiz",
        "description": "AI-generated quiz",
        "pass_percentage": 70,
        "questions": [
            {
                "prompt": f"Sample question {index}",
                "options": [
                    "Option A",
                    "Option B",
                    "Option C",
                    "Option D"
                ],
                "correct_answer": "Option A",
                "explanation": "Fallback question.",
                "order_index": index
            }
            for index in range(1, QUIZ_QUESTION_COUNT + 1)
        ]
    }


def generate_quiz_payload(lesson_title, lesson_content):
    prompt = build_quiz_prompt(
        lesson_title,
        lesson_content
    )

    return generate_json(
        prompt,
        lambda: _fallback_quiz(lesson_title)
    )
