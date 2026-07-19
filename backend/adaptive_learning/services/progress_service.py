from datetime import datetime

from adaptive_learning.extensions import db
from adaptive_learning.models.course import Course
from adaptive_learning.models.lesson import Lesson
from adaptive_learning.models.progress import Progress
from adaptive_learning.models.student_learning_method_result import StudentLearningMethodResult
from adaptive_learning.models.student_learning_profile import StudentLearningProfile
from adaptive_learning.services import adaptive_learning_service

VALID_PROGRESS_STATUSES = {
    "not_started",
    "in_progress",
    "completed"
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


def _serialize_progress(progress):
    return {
        "id": progress.id,
        "user_id": progress.user_id,
        "lesson_id": progress.lesson_id,
        "status": progress.status,
        "completion_percentage": progress.completion_percentage,
        "current_learning_stage": progress.current_learning_stage,
        "last_accessed_at": progress.last_accessed_at.isoformat(),
        "completed_at": (
            progress.completed_at.isoformat()
            if progress.completed_at
            else None
        ),
        "created_at": progress.created_at.isoformat(),
        "updated_at": progress.updated_at.isoformat()
    }


def _serialize_lesson_progress(lesson, progress):
    return {
        "lesson": {
            "id": lesson.id,
            "course_id": lesson.course_id,
            "title": lesson.title,
            "slug": lesson.slug,
            "order_index": lesson.order_index,
            "estimated_minutes": lesson.estimated_minutes
        },
        "progress": (
            _serialize_progress(progress)
            if progress
            else {
        "status": "not_started",
        "completion_percentage": 0,
        "current_learning_stage": "material",
        "last_accessed_at": None,
        "completed_at": None
            }
        )
    }


def _get_visible_course(course_id, role):
    course = db.session.get(Course, course_id)

    if not course:
        return None, _failure("Course not found", 404)

    if role != "admin" and not course.is_published:
        return None, _failure("Course not found", 404)

    return course, None


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


def _get_course_lessons(course, role):
    query = Lesson.query.filter_by(course_id=course.id).order_by(
        Lesson.order_index.asc(),
        Lesson.created_at.asc()
    )

    if role != "admin":
        query = query.filter_by(is_published=True)

    return query.all()


def _build_course_summary(course, lessons, progress_by_lesson_id):
    total_lessons = len(lessons)
    completed_lessons = 0
    in_progress_lessons = 0
    total_completion = 0

    for lesson in lessons:
        progress = progress_by_lesson_id.get(lesson.id)
        completion_percentage = (
            progress.completion_percentage if progress else 0
        )
        total_completion += completion_percentage

        if progress and progress.status == "completed":
            completed_lessons += 1
        elif progress and progress.status == "in_progress":
            in_progress_lessons += 1

    overall_completion = (
        round(total_completion / total_lessons)
        if total_lessons
        else 0
    )

    return {
        "course": {
            "id": course.id,
            "title": course.title,
            "slug": course.slug
        },
        "summary": {
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "in_progress_lessons": in_progress_lessons,
            "overall_completion_percentage": overall_completion
        }
    }


def _validate_progress_update(data):
    data = data or {}

    if not data:
        return _failure("Progress update data is required")

    if "status" not in data and "completion_percentage" not in data:
        return _failure(
            "status or completion_percentage is required"
        )

    status = data.get("status")
    if status is not None:
        status = str(status).strip().lower()
        if status not in VALID_PROGRESS_STATUSES:
            return _failure(
                "Status must be not_started, in_progress, or completed"
            )

    completion_percentage = data.get("completion_percentage")
    if completion_percentage is not None:
        try:
            completion_percentage = int(completion_percentage)
        except (TypeError, ValueError):
            return _failure(
                "completion_percentage must be a valid integer"
            )

        if completion_percentage < 0 or completion_percentage > 100:
            return _failure(
                "completion_percentage must be between 0 and 100"
            )

    return {
        "status": status,
        "completion_percentage": completion_percentage
    }, 200


def get_course_progress(user_id, course_id, role):
    course, error = _get_visible_course(course_id, role)
    if error:
        return error

    lessons = _get_course_lessons(course, role)
    lesson_ids = [lesson.id for lesson in lessons]

    progress_records = []
    if lesson_ids:
        progress_records = Progress.query.filter(
            Progress.user_id == int(user_id),
            Progress.lesson_id.in_(lesson_ids)
        ).all()

    progress_by_lesson_id = {
        record.lesson_id: record for record in progress_records
    }

    course_summary = _build_course_summary(
        course,
        lessons,
        progress_by_lesson_id
    )
    course_summary["lessons"] = [
        _serialize_lesson_progress(
            lesson,
            progress_by_lesson_id.get(lesson.id)
        )
        for lesson in lessons
    ]

    return _success(
        "Course progress retrieved successfully",
        course_summary
    )


def get_progress_overview(user_id, role):
    query = Course.query.order_by(Course.created_at.desc())

    if role != "admin":
        query = query.filter_by(is_published=True)

    courses = query.all()
    overview = []

    for course in courses:
        lessons = _get_course_lessons(course, role)
        lesson_ids = [lesson.id for lesson in lessons]

        progress_records = []
        if lesson_ids:
            progress_records = Progress.query.filter(
                Progress.user_id == int(user_id),
                Progress.lesson_id.in_(lesson_ids)
            ).all()

        progress_by_lesson_id = {
            record.lesson_id: record for record in progress_records
        }
        overview.append(
            _build_course_summary(course, lessons, progress_by_lesson_id)
        )

    return _success(
        "Progress overview retrieved successfully",
        {"courses": overview}
    )

def get_lesson_progress(user_id, lesson_id, role):
    lesson, error = _get_visible_lesson(lesson_id, role)
    if error:
        return error

    progress = Progress.query.filter_by(
        user_id=int(user_id),
        lesson_id=lesson.id
    ).first()

    return _success(
        "Lesson progress retrieved successfully",
        {
            "lesson": {
                "id": lesson.id,
                "title": lesson.title,
                "course_id": lesson.course_id
            },
            "progress": (
                _serialize_progress(progress)
                if progress
                else {
                    "status": "not_started",
                    "completion_percentage": 0,
                    "current_learning_stage": "material",
                    "last_accessed_at": None,
                    "completed_at": None
                }
            )
        }
    )



def update_lesson_progress(user_id, lesson_id, role, data):
    lesson, error = _get_visible_lesson(lesson_id, role)
    if error:
        return error

    validation_result, status_code = _validate_progress_update(data)
    if status_code != 200:
        return validation_result, status_code

    progress = Progress.query.filter_by(
        user_id=int(user_id),
        lesson_id=lesson.id
    ).first()

    if not progress:
        progress = Progress(
            user_id=int(user_id),
            lesson_id=lesson.id,
            current_learning_stage="material"
        )
        db.session.add(progress)

    status = validation_result["status"]
    completion_percentage = validation_result["completion_percentage"]

    if status is None and completion_percentage is not None:
        if completion_percentage == 0:
            status = "not_started"
        elif completion_percentage == 100:
            status = "completed"
        else:
            status = "in_progress"

    if completion_percentage is None and status is not None:
        if status == "not_started":
            completion_percentage = 0
        elif status == "completed":
            completion_percentage = 100
        else:
            completion_percentage = max(progress.completion_percentage, 1)
            if completion_percentage >= 100:
                completion_percentage = 99

    progress.status = status or progress.status
    progress.completion_percentage = (
        completion_percentage
        if completion_percentage is not None
        else progress.completion_percentage
    )
    progress.last_accessed_at = datetime.utcnow()

    if progress.status == "not_started":
        progress.current_learning_stage = "material"

    elif progress.status == "completed":
        progress.current_learning_stage = "completed"

    if progress.status == "completed":
        progress.completion_percentage = 100
        progress.completed_at = datetime.utcnow()
    else:
        progress.completed_at = None

    if progress.status == "not_started":
        progress.completion_percentage = 0

    db.session.commit()    

    return _success(
        "Lesson progress updated successfully",
        {
            "lesson": {
                "id": lesson.id,
                "title": lesson.title,
                "course_id": lesson.course_id
            },
            "progress": _serialize_progress(progress)
        }
    )

def reset_lesson_progress(user_id, lesson_id):
    user_id = int(user_id)

    # Delete lesson progress
    progress = Progress.query.filter_by(
        user_id=user_id,
        lesson_id=lesson_id
    ).first()

    if progress:
        db.session.delete(progress)

    # Delete adaptive learning history for this lesson
    StudentLearningMethodResult.query.filter_by(
        student_id=user_id,
        lesson_id=lesson_id
    ).delete()

    remaining_results = StudentLearningMethodResult.query.filter_by(
        student_id=user_id
    ).count()

    if remaining_results:
        adaptive_learning_service.sync_learning_profile(user_id)
    else:
        profile = StudentLearningProfile.query.filter_by(
            student_id=user_id
        ).first()

        if profile:
            db.session.delete(profile)

    db.session.commit()

    return _success("Lesson progress reset")
