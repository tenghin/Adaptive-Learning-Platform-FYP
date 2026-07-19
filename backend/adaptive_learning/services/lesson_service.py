import re
import os

from werkzeug.utils import secure_filename
from flask import current_app
from flask import send_file

from adaptive_learning.extensions import db
from adaptive_learning.models.course import Course
from adaptive_learning.models.lesson import Lesson
from adaptive_learning.models.lesson_resource import LessonResource


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


def _slugify(value):
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "lesson"


def _generate_unique_slug(course_id, title, excluded_lesson_id=None):
    base_slug = _slugify(title)
    slug = base_slug
    counter = 2

    while True:
        query = Lesson.query.filter_by(course_id=course_id, slug=slug)
        if excluded_lesson_id is not None:
            query = query.filter(Lesson.id != excluded_lesson_id)

        if not query.first():
            return slug

        slug = f"{base_slug}-{counter}"
        counter += 1


def _serialize_lesson(lesson, include_content=True):
    payload = {
        "id": lesson.id,
        "course_id": lesson.course_id,
        "title": lesson.title,
        "slug": lesson.slug,
        "summary": lesson.summary,
        "order_index": lesson.order_index,
        "estimated_minutes": lesson.estimated_minutes,
        "is_published": lesson.is_published,
        "created_at": lesson.created_at.isoformat(),
        "updated_at": lesson.updated_at.isoformat()
    }

    if include_content:
        payload["content"] = lesson.content

    return payload


def _serialize_lesson_resource(resource):
    return {
        "id": resource.id,
        "lesson_id": resource.lesson_id,
        "title": resource.title,
        "resource_type": resource.resource_type,
        "content": resource.content,
        "file_name": resource.file_name,
        "file_path": resource.file_path,
        "mime_type": resource.mime_type,
        "is_generated": resource.is_generated,
        "is_published": resource.is_published,
        "created_at": resource.created_at.isoformat(),
        "updated_at": resource.updated_at.isoformat()
    }


def _validate_lesson_data(data, partial=False):
    data = data or {}
    required_fields = ["title", "content"]

    if partial and not data:
        return _failure("At least one field is required to update a lesson")

    if not partial:
        missing_fields = []
        for field in required_fields:
            value = data.get(field)
            if value is None or not str(value).strip():
                missing_fields.append(field)

        if missing_fields:
            return _failure(
                f"Missing required fields: {', '.join(missing_fields)}"
            )

    title = str(data.get("title", "")).strip()
    content = str(data.get("content", "")).strip()

    summary = None
    if "summary" in data or not partial:
        summary = data.get("summary")
        if summary is not None:
            summary = str(summary).strip() or None

    order_index = None
    if "order_index" in data or not partial:
        order_index = data.get("order_index", 1)

    estimated_minutes = None
    if "estimated_minutes" in data or not partial:
        estimated_minutes = data.get("estimated_minutes", 15)

    is_published = None
    if "is_published" in data or not partial:
        is_published = data.get("is_published", True)

    if "title" in data and not title:
        return _failure("Lesson title is required")

    if "content" in data and not content:
        return _failure("Lesson content is required")

    if order_index is not None:
        try:
            order_index = int(order_index)
        except (TypeError, ValueError):
            return _failure("order_index must be a valid integer")

        if order_index <= 0:
            return _failure("order_index must be greater than zero")

    if estimated_minutes is not None:
        try:
            estimated_minutes = int(estimated_minutes)
        except (TypeError, ValueError):
            return _failure("Estimated minutes must be a valid integer")

        if estimated_minutes <= 0:
            return _failure("Estimated minutes must be greater than zero")

    if is_published is not None and not isinstance(is_published, bool):
        return _failure("is_published must be true or false")

    return {
        "title": title,
        "content": content,
        "summary": summary,
        "order_index": order_index,
        "estimated_minutes": estimated_minutes,
        "is_published": is_published
    }, 200


def _get_course_or_404(course_id, role):
    course = db.session.get(Course, course_id)

    if not course:
        return None, _failure("Course not found", 404)

    if not course.is_published and role != "admin":
        return None, _failure("Course not found", 404)

    return course, None

def _lesson_order_exists(course_id, order_index, excluded_lesson_id=None):
    query = Lesson.query.filter_by(
        course_id=course_id,
        order_index=order_index
    )

    if excluded_lesson_id is not None:
        query = query.filter(
            Lesson.id != excluded_lesson_id
        )

    return query.first() is not None


def _get_visible_lesson_resource(resource_id, role):
    resource = db.session.get(LessonResource, resource_id)

    if not resource:
        return None, _failure("Lesson resource not found", 404)

    lesson = resource.lesson
    if role != "admin" and (
        not resource.is_published
        or not lesson.is_published
        or not lesson.course.is_published
    ):
        return None, _failure("Lesson resource not found", 404)

    return resource, None


def list_lessons(course_id, role):
    course, error = _get_course_or_404(course_id, role)
    if error:
        return error

    query = Lesson.query.filter_by(course_id=course.id).order_by(
        Lesson.order_index.asc(),
        Lesson.created_at.asc()
    )

    if role != "admin":
        query = query.filter_by(is_published=True)

    lessons = query.all()

    return _success(
        "Lessons retrieved successfully",
        {
            "course": {
                "id": course.id,
                "title": course.title,
                "slug": course.slug
            },
            "lessons": [
                _serialize_lesson(lesson, include_content=False)
                for lesson in lessons
            ]
        }
    )


def get_lesson(lesson_id, role):
    lesson = db.session.get(Lesson, lesson_id)

    if not lesson:
        return _failure("Lesson not found", 404)

    if (
        role != "admin"
        and (
            not lesson.is_published
            or not lesson.course.is_published
        )
    ):
        return _failure("Lesson not found", 404)

    return _success(
        "Lesson retrieved successfully",
        {"lesson": _serialize_lesson(lesson)}
    )


def create_lesson(course_id, data, role):
    data = data or {}
    admin_error = _validate_admin(role)
    if admin_error:
        return admin_error

    course = db.session.get(Course, course_id)
    if not course:
        return _failure("Course not found", 404)

    validation_result, status_code = _validate_lesson_data(data)
    if status_code != 200:
        return validation_result, status_code
    
    if _lesson_order_exists(
        course.id,
        validation_result["order_index"]
    ):
        return _failure(
            "Another lesson already uses this lesson order.",
            400
        )

    lesson = Lesson(
        course_id=course.id,
        title=validation_result["title"],
        slug=_generate_unique_slug(course.id, validation_result["title"]),
        content=validation_result["content"],
        summary=validation_result["summary"],
        order_index=validation_result["order_index"],
        estimated_minutes=validation_result["estimated_minutes"],
        is_published=validation_result["is_published"]
    )

    db.session.add(lesson)
    db.session.commit()

    return _success(
        "Lesson created successfully",
        {"lesson": _serialize_lesson(lesson)},
        201
    )


def update_lesson(lesson_id, data, role):
    data = data or {}
    admin_error = _validate_admin(role)
    if admin_error:
        return admin_error

    lesson = db.session.get(Lesson, lesson_id)
    if not lesson:
        return _failure("Lesson not found", 404)

    validation_result, status_code = _validate_lesson_data(
        data,
        partial=True
    )
    if status_code != 200:
        return validation_result, status_code

    if (
        "order_index" in data
        and _lesson_order_exists(
            lesson.course_id,
            validation_result["order_index"],
            excluded_lesson_id=lesson.id
        )
    ):
        return _failure(
            f"Lesson order {validation_result['order_index']} is already used in this course.",
            400
        )

    if "title" in data:
        lesson.title = validation_result["title"]
        lesson.slug = _generate_unique_slug(
            lesson.course_id,
            validation_result["title"],
            excluded_lesson_id=lesson.id
        )

    if "content" in data:
        lesson.content = validation_result["content"]

    if "summary" in data:
        lesson.summary = validation_result["summary"]

    if "order_index" in data:
        lesson.order_index = validation_result["order_index"]

    if "estimated_minutes" in data:
        lesson.estimated_minutes = validation_result["estimated_minutes"]

    if "is_published" in data:
        lesson.is_published = validation_result["is_published"]

    db.session.commit()

    return _success(
        "Lesson updated successfully",
        {"lesson": _serialize_lesson(lesson)}
    )


def delete_lesson(lesson_id, role):
    admin_error = _validate_admin(role)
    if admin_error:
        return admin_error

    lesson = db.session.get(Lesson, lesson_id)
    if not lesson:
        return _failure("Lesson not found", 404)

    db.session.delete(lesson)
    db.session.commit()

    return _success("Lesson deleted successfully")


def _validate_lesson_resource_data(data, partial=False):
    data = data or {}

    if partial and not data:
        return _failure(
            "At least one field is required to update a lesson resource"
        )

    title = str(data.get("title", "")).strip()
    content = str(data.get("content", "")).strip()
    resource_type = data.get("resource_type")
    file_name = data.get("file_name")
    file_path = data.get("file_path")
    mime_type = data.get("mime_type")
    is_generated = data.get("is_generated")
    is_published = data.get("is_published")

    if not partial and not title:
        return _failure("Lesson resource title is required")

    if not partial and not content:
        return _failure("Lesson resource content is required")

    if "title" in data and not title:
        return _failure("Lesson resource title is required")

    if "content" in data and not content:
        return _failure("Lesson resource content is required")

    if resource_type is not None:
        resource_type = str(resource_type).strip().lower()
        if not resource_type:
            return _failure("resource_type cannot be empty")

    if file_name is not None:
        file_name = str(file_name).strip() or None

    if file_path is not None:
        file_path = str(file_path).strip() or None

    if mime_type is not None:
        mime_type = str(mime_type).strip() or None

    if is_generated is not None and not isinstance(is_generated, bool):
        return _failure("is_generated must be true or false")

    if is_published is not None and not isinstance(is_published, bool):
        return _failure("is_published must be true or false")

    return {
        "title": title,
        "content": content,
        "resource_type": resource_type,
        "file_name": file_name,
        "file_path": file_path,
        "mime_type": mime_type,
        "is_generated": is_generated,
        "is_published": is_published
    }, 200


def list_lesson_resources(lesson_id, role):
    lesson = db.session.get(Lesson, lesson_id)

    if not lesson:
        return _failure("Lesson not found", 404)

    if role != "admin" and (
        not lesson.is_published
        or not lesson.course.is_published
    ):
        return _failure("Lesson not found", 404)

    query = LessonResource.query.filter_by(lesson_id=lesson.id).order_by(
        LessonResource.created_at.desc()
    )

    if role != "admin":
        query = query.filter_by(is_published=True)

    resources = query.all()

    return _success(
        "Lesson resources retrieved successfully",
        {
            "lesson": {
                "id": lesson.id,
                "title": lesson.title,
                "slug": lesson.slug
            },
            "resources": [
                _serialize_lesson_resource(resource)
                for resource in resources
            ]
        }
    )


def get_lesson_resource(resource_id, role):
    resource, error = _get_visible_lesson_resource(resource_id, role)
    if error:
        return error

    return _success(
        "Lesson resource retrieved successfully",
        {"resource": _serialize_lesson_resource(resource)}
    )


def create_lesson_resource(lesson_id, data, role):
    data = data or {}
    admin_error = _validate_admin(role)
    if admin_error:
        return admin_error

    lesson = db.session.get(Lesson, lesson_id)
    if not lesson:
        return _failure("Lesson not found", 404)

    validation_result, status_code = _validate_lesson_resource_data(data)
    if status_code != 200:
        return validation_result, status_code

    resource = LessonResource(
        lesson_id=lesson.id,
        title=validation_result["title"],
        resource_type=validation_result["resource_type"] or "material",
        content=validation_result["content"],
        file_name=validation_result["file_name"],
        file_path=validation_result["file_path"],
        mime_type=validation_result["mime_type"],
        is_generated=(
            validation_result["is_generated"]
            if validation_result["is_generated"] is not None
            else False
        ),
        is_published=(
            validation_result["is_published"]
            if validation_result["is_published"] is not None
            else True
        )
    )

    db.session.add(resource)
    db.session.commit()

    return _success(
        "Lesson resource created successfully",
        {"resource": _serialize_lesson_resource(resource)},
        201
    )


def update_lesson_resource(resource_id, data, role):
    data = data or {}
    admin_error = _validate_admin(role)
    if admin_error:
        return admin_error

    resource = db.session.get(LessonResource, resource_id)
    if not resource:
        return _failure("Lesson resource not found", 404)

    validation_result, status_code = _validate_lesson_resource_data(
        data,
        partial=True
    )
    if status_code != 200:
        return validation_result, status_code

    if "title" in data:
        resource.title = validation_result["title"]

    if "content" in data:
        resource.content = validation_result["content"]

    if "resource_type" in data:
        resource.resource_type = (
            validation_result["resource_type"] or resource.resource_type
        )

    if "file_name" in data:
        resource.file_name = validation_result["file_name"]

    if "file_path" in data:
        resource.file_path = validation_result["file_path"]

    if "mime_type" in data:
        resource.mime_type = validation_result["mime_type"]

    if "is_generated" in data:
        resource.is_generated = validation_result["is_generated"]

    if "is_published" in data:
        resource.is_published = validation_result["is_published"]

    db.session.commit()

    return _success(
        "Lesson resource updated successfully",
        {"resource": _serialize_lesson_resource(resource)}
    )


def delete_lesson_resource(resource_id, role):
    admin_error = _validate_admin(role)
    if admin_error:
        return admin_error

    resource = db.session.get(LessonResource, resource_id)
    if not resource:
        return _failure("Lesson resource not found", 404)

    db.session.delete(resource)
    db.session.commit()

    return _success("Lesson resource deleted successfully")

def upload_learning_material(lesson_id, file, title, role):
    admin_error = _validate_admin(role)
    if admin_error:
        return admin_error

    lesson = db.session.get(Lesson, lesson_id)
    if not lesson:
        return _failure("Lesson not found", 404)

    if file is None:
        return _failure("No file uploaded")

    filename = secure_filename(file.filename)

    if not filename:
        return _failure("Invalid file name")

    lesson_folder = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        f"lesson_{lesson.id}"
    )

    os.makedirs(
        lesson_folder,
        exist_ok=True
    )

    file_path = os.path.join(
        lesson_folder,
        filename
    )

    file.save(file_path)

    resource = LessonResource(
        lesson_id=lesson.id,
        title=title or filename,
        resource_type="material",
        content="",
        file_name=filename,
        file_path=file_path,
        mime_type=file.mimetype,
        is_generated=False,
        is_published=True,
    )

    db.session.add(resource)
    db.session.commit()

    return _success(
        "Learning material uploaded successfully",
        {
            "resource": _serialize_lesson_resource(resource)
        },
        201
    )

def download_lesson_resource(resource_id, role):
    resource, error = _get_visible_lesson_resource(resource_id, role)
    if error:
        return error

    if not resource.file_path:
        return _failure("No file available", 404)

    return send_file(
        resource.file_path,
        as_attachment=False
    )
