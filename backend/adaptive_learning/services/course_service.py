import re

from adaptive_learning.extensions import db
from adaptive_learning.models.course import Course


VALID_DIFFICULTY_LEVELS = {
    "beginner",
    "intermediate",
    "advanced"
}


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


def _serialize_course(course, include_lessons=False):
    result = {
        "id": course.id,
        "title": course.title,
        "slug": course.slug,
        "description": course.description,
        "difficulty_level": course.difficulty_level,
        "estimated_minutes": course.estimated_minutes,
        "is_published": course.is_published,
        "created_at": course.created_at.isoformat(),
        "updated_at": course.updated_at.isoformat(),
    }

    if include_lessons:
        result["lessons"] = [
            {
                "id": lesson.id,
                "title": lesson.title,
                "order_index": lesson.order_index,
                "is_published": lesson.is_published,
            }
            for lesson in sorted(
                course.lessons,
                key=lambda lesson: lesson.order_index,
            )
        ]

    return result


def _slugify(value):
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "course"


def _generate_unique_slug(title, excluded_course_id=None):
    base_slug = _slugify(title)
    slug = base_slug
    counter = 2

    while True:
        query = Course.query.filter_by(slug=slug)
        if excluded_course_id is not None:
            query = query.filter(Course.id != excluded_course_id)

        if not query.first():
            return slug

        slug = f"{base_slug}-{counter}"
        counter += 1


def _validate_admin(role):
    if role != "admin":
        return _failure("Administrator access is required", 403)
    return None


def _validate_course_data(data, partial=False):
    data = data or {}
    required_fields = ["title", "description"]

    if partial and not data:
        return _failure("At least one field is required to update a course")

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
    description = str(data.get("description", "")).strip()

    difficulty_level = None
    if "difficulty_level" in data or not partial:
        difficulty_level = str(
            data.get("difficulty_level", "beginner")
        ).strip().lower()

    estimated_minutes = None
    if "estimated_minutes" in data or not partial:
        estimated_minutes = data.get("estimated_minutes", 60)

    is_published = None
    if "is_published" in data or not partial:
        is_published = data.get("is_published", True)

    if "title" in data and not title:
        return _failure("Course title is required")

    if "description" in data and not description:
        return _failure("Course description is required")

    if difficulty_level is not None and difficulty_level not in VALID_DIFFICULTY_LEVELS:
        return _failure(
            "Difficulty level must be beginner, intermediate, or advanced"
        )

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
        "description": description,
        "difficulty_level": difficulty_level,
        "estimated_minutes": estimated_minutes,
        "is_published": is_published
    }, 200


def list_courses(role):
    query = Course.query.order_by(Course.created_at.desc())

    if role != "admin":
        query = query.filter_by(is_published=True)

    courses = query.all()

    return _success(
        "Courses retrieved successfully",
        {"courses": [_serialize_course(course) for course in courses]}
    )


def get_course(course_id, role):
    course = db.session.get(Course, course_id)

    if not course:
        return _failure("Course not found", 404)

    if not course.is_published and role != "admin":
        return _failure("Course not found", 404)

    return _success(
        "Course retrieved successfully",
        {
            "course": _serialize_course(
                course,
                include_lessons=True
            )
        }
    )


def create_course(data, role):
    data = data or {}
    admin_error = _validate_admin(role)
    if admin_error:
        return admin_error

    validation_result, status_code = _validate_course_data(data)
    if status_code != 200:
        return validation_result, status_code

    course = Course(
        title=validation_result["title"],
        slug=_generate_unique_slug(validation_result["title"]),
        description=validation_result["description"],
        difficulty_level=validation_result["difficulty_level"],
        estimated_minutes=validation_result["estimated_minutes"],
        is_published=validation_result["is_published"]
    )

    db.session.add(course)
    db.session.commit()

    return _success(
        "Course created successfully",
        {"course": _serialize_course(course)},
        201
    )


def update_course(course_id, data, role):
    data = data or {}
    admin_error = _validate_admin(role)
    if admin_error:
        return admin_error

    course = db.session.get(Course, course_id)
    if not course:
        return _failure("Course not found", 404)

    validation_result, status_code = _validate_course_data(
        data,
        partial=True
    )
    if status_code != 200:
        return validation_result, status_code

    if "title" in data:
        course.title = validation_result["title"]
        course.slug = _generate_unique_slug(
            validation_result["title"],
            excluded_course_id=course.id
        )

    if "description" in data:
        course.description = validation_result["description"]

    if "difficulty_level" in data:
        course.difficulty_level = validation_result["difficulty_level"]

    if "estimated_minutes" in data:
        course.estimated_minutes = validation_result["estimated_minutes"]

    if "is_published" in data:
        course.is_published = validation_result["is_published"]

    db.session.commit()

    return _success(
        "Course updated successfully",
        {"course": _serialize_course(course)}
    )


def delete_course(course_id, role):
    admin_error = _validate_admin(role)
    if admin_error:
        return admin_error

    course = db.session.get(Course, course_id)
    if not course:
        return _failure("Course not found", 404)

    db.session.delete(course)
    db.session.commit()

    return _success("Course deleted successfully")
