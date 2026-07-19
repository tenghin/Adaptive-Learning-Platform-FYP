import json

from adaptive_learning.ai.gemini_client import (
    generate_knowledge_graph_payload,
    generate_summary_payload,
)
from adaptive_learning.ai.prompt_builder import (
    build_knowledge_graph_prompt,
    build_summary_prompt,
)
from adaptive_learning.ai.schemas import (
    validate_knowledge_graph_payload,
    validate_summary_payload,
)
from adaptive_learning.extensions import db
from adaptive_learning.models.lesson import Lesson
from adaptive_learning.models.lesson_resource import LessonResource
from adaptive_learning.ai.document_reader import extract_text

def _success(message, data=None, status_code=200):
    return {
        "success": True,
        "message": message,
        "data": data or {}
    }, status_code


def _failure(message, status_code=400):
    return {
        "success": False,
        "message": message
    }, status_code


def _validate_admin(role):
    if role != "admin":
        return _failure("Administrator access is required", 403)
    return None


def _get_visible_lesson(lesson_id, role):
    lesson = db.session.get(Lesson, lesson_id)

    if not lesson:
        return None, _failure("Lesson not found", 404)

    if role != "admin" and (
        not lesson.is_published
        or not lesson.course.is_published
    ):
        return None, _failure("Lesson not found", 404)

    return lesson, None


def _serialize_resource(resource):
    return {
        "id": resource.id,
        "lesson_id": resource.lesson_id,
        "title": resource.title,
        "resource_type": resource.resource_type,
        "content": resource.content,
        "file_name": resource.file_name,
        "mime_type": resource.mime_type,
        "is_generated": resource.is_generated,
        "is_published": resource.is_published,
        "created_at": resource.created_at.isoformat(),
        "updated_at": resource.updated_at.isoformat(),
    }


def _upsert_generated_resource(lesson, title, resource_type, content):
    existing_resource = LessonResource.query.filter_by(
        lesson_id=lesson.id,
        resource_type=resource_type,
        is_generated=True
    ).first()

    content_as_text = json.dumps(content, ensure_ascii=False)

    if existing_resource:
        existing_resource.title = title
        existing_resource.content = content_as_text
        existing_resource.is_published = True
        resource = existing_resource
    else:
        resource = LessonResource(
            lesson_id=lesson.id,
            title=title,
            resource_type=resource_type,
            content=content_as_text,
            is_generated=True,
            is_published=True
        )
        db.session.add(resource)

    return resource

def _get_lesson_text(lesson):
    lesson_text = lesson.content

    material = LessonResource.query.filter_by(
        lesson_id=lesson.id,
        resource_type="material"
    ).first()

    if material:
        lesson_text = extract_text(material.file_path)

    return lesson_text

def generate_lesson_summary(lesson_id, role):
    
    lesson, error = _get_visible_lesson(lesson_id, role)
    if error:
        return error

    lesson_text = _get_lesson_text(lesson)

    prompt = build_summary_prompt(
        lesson.title,
        lesson_text
    )

    payload, fallback_error = generate_summary_payload(
        prompt,
        lambda: {
            "summary": lesson.content.split(".")[0].strip()
            or f"This lesson covers {lesson.title}."
        }
    )

    validation_result, validation_error = validate_summary_payload(payload)

    if validation_error:
        return _failure(validation_error, 502)

    lesson.summary = validation_result["summary"]

    resource = _upsert_generated_resource(
        lesson,
        f"{lesson.title} Summary",
        "summary",
        validation_result
    )

    db.session.commit()

    return _success(
        "Lesson summary generated successfully",
        {
            "lesson": {
                "id": lesson.id,
                "title": lesson.title,
                "summary": lesson.summary,
            },
            "resource": _serialize_resource(resource),
            "generation_source": "fallback" if fallback_error else "gemini",
        },
        201
    )


def generate_lesson_knowledge_graph(lesson_id, role):

    lesson, error = _get_visible_lesson(lesson_id, role)
    if error:
        return error

    lesson_text = _get_lesson_text(lesson)

    prompt = build_knowledge_graph_prompt(
        lesson.title,
        lesson_text
    )

    payload, fallback_error = generate_knowledge_graph_payload(
        prompt,
        lambda: {
            "lesson_title": lesson.title,
            "concepts": [],
            "relationships": []
        }
    )
    
    validation_result, validation_error = validate_knowledge_graph_payload(
        payload
    )

    if validation_error:
        return _failure(validation_error, 502)

    resource = _upsert_generated_resource(
        lesson,
        f"{lesson.title} Knowledge Graph",
        "knowledge_graph",
        validation_result
    )

    db.session.commit()

    return _success(
        "Knowledge graph generated successfully",
        {
            "lesson": {
                "id": lesson.id,
                "title": lesson.title,
            },
            "knowledge_graph": validation_result,
            "resource": _serialize_resource(resource),
            "generation_source": "fallback" if fallback_error else "gemini",
        },
        201
    )
