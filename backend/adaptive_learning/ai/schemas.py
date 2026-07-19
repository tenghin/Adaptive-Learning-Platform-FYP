import json


def _ensure_dict(value):
    if isinstance(value, dict):
        return value, None

    if isinstance(value, str):
        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            return None, "Response must be valid JSON"

        if isinstance(parsed_value, dict):
            return parsed_value, None

    return None, "Response must be a JSON object"


def validate_summary_payload(value):
    payload, error = _ensure_dict(value)
    if error:
        return None, error

    summary = str(payload.get("summary", "")).strip()
    if not summary:
        return None, "summary is required"

    return {"summary": summary}, None


def validate_knowledge_graph_payload(value):
    payload, error = _ensure_dict(value)
    if error:
        return None, error

    lesson_title = str(payload.get("lesson_title")or payload.get("title", "")).strip()
    concepts = payload.get("concepts")
    relationships = payload.get("relationships")

    if not lesson_title:
        return None, "lesson_title is required"

    if not isinstance(concepts, list):
        return None, "concepts must be a list"

    if not isinstance(relationships, list):
        return None, "relationships must be a list"

    normalized_concepts = []
    for concept in concepts:
        if not isinstance(concept, dict):
            return None, "Each concept must be an object"

        concept_id = str(concept.get("id", "")).strip()
        label = str(concept.get("label", "")).strip()
        description = str(concept.get("description", "")).strip()

        if not concept_id or not label:
            return None, "Each concept requires id and label"

        normalized_concepts.append(
            {
                "id": concept_id,
                "label": label,
                "description": description or None,
            }
        )

    normalized_relationships = []
    allowed_types = {"prerequisite", "related_to", "part_of", "causes"}
    for relationship in relationships:
        if not isinstance(relationship, dict):
            return None, "Each relationship must be an object"

        source = str(relationship.get("source", "")).strip()
        target = str(relationship.get("target", "")).strip()
        relation_type = str(
            relationship.get("type", "related_to")
        ).strip().lower()

        if not source or not target:
            return None, "Each relationship requires source and target"

        if relation_type not in allowed_types:
            relation_type = "related_to"

        normalized_relationships.append(
            {
                "source": source,
                "target": target,
                "type": relation_type,
            }
        )

    return {
        "lesson_title": lesson_title,
        "concepts": normalized_concepts,
        "relationships": normalized_relationships,
    }, None

def validate_quiz_payload(value):
    payload, error = _ensure_dict(value)
    if error:
        return None, error

    title = str(payload.get("title", "")).strip()
    description = str(payload.get("description", "")).strip()

    pass_percentage = payload.get("pass_percentage", 70)

    try:
        pass_percentage = int(pass_percentage)
    except (TypeError, ValueError):
        return None, "pass_percentage must be an integer"

    questions = payload.get("questions")

    if not title:
        return None, "title is required"

    if not isinstance(questions, list) or not questions:
        return None, "questions are required"

    normalized_questions = []

    for index, question in enumerate(questions, start=1):

        if not isinstance(question, dict):
            return None, f"Question {index} must be an object"

        prompt = str(question.get("prompt", "")).strip()
        options = question.get("options", [])
        correct_answer = str(question.get("correct_answer", "")).strip()
        explanation = str(question.get("explanation", "")).strip()

        if not prompt:
            return None, f"Question {index} prompt is required"

        if not isinstance(options, list) or len(options) != 4:
            return None, f"Question {index} must contain exactly four options"

        if correct_answer not in options:
            return None, f"Question {index} correct_answer must match one option"

        normalized_questions.append(
            {
                "prompt": prompt,
                "options": options,
                "correct_answer": correct_answer,
                "explanation": explanation,
                "order_index": index,
            }
        )

    return {
        "title": title,
        "description": description,
        "pass_percentage": pass_percentage,
        "questions": normalized_questions,
    }, None