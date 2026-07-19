from adaptive_learning.extensions import db
from adaptive_learning.models.lesson import Lesson
from adaptive_learning.models.progress import Progress
from adaptive_learning.services import adaptive_learning_service
from datetime import datetime


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

def _build_recommendation_payload(lesson, user_id, profile, lesson_results):
    method_metrics = adaptive_learning_service.get_learning_method_metrics(user_id)
    used_methods = [result.learning_method for result in lesson_results]
    last_result = lesson_results[-1] if lesson_results else None
    remaining_methods = [
        method
        for method in adaptive_learning_service.get_available_learning_methods(lesson)
        if method not in used_methods
    ]

    if last_result and last_result.passed:
        return {
            "recommended_method": "next_lesson",
            "title": "Lesson Completed",
            "reason": "You passed the quiz. Move on to the next lesson.",
            "used_methods": used_methods,
            "remaining_methods": remaining_methods,
            "attempt_count": len(lesson_results),
            "lesson_completed": True,
        }

    if not lesson_results:
        initial_method = adaptive_learning_service.choose_initial_learning_method(
            lesson,
            user_id,
            profile,
        )

        if not initial_method:
            return {
                "recommended_method": "material",
                "title": "Review the Lesson Material",
                "reason": "No adaptive learning content is available yet, so start with the original material.",
                "used_methods": [],
                "remaining_methods": [],
                "attempt_count": 0,
                "lesson_completed": False,
            }

        return {
            "recommended_method": initial_method,
            "title": _get_learning_method_title(initial_method),
            "reason": _build_method_reason(
                initial_method,
                profile,
                method_metrics,
                is_first_attempt=True,
            ),
            "used_methods": used_methods,
            "remaining_methods": [
                method for method in remaining_methods
                if method != initial_method
            ],
            "attempt_count": 0,
            "lesson_completed": False,
        }

    next_method = adaptive_learning_service.choose_next_learning_method(
        lesson,
        user_id,
        profile,
        used_methods,
    )

    if next_method:
        return {
            "recommended_method": next_method,
            "title": _get_learning_method_title(next_method),
            "reason": _build_method_reason(
                next_method,
                profile,
                method_metrics,
                previous_result=last_result,
            ),
            "used_methods": used_methods,
            "remaining_methods": [
                method for method in remaining_methods
                if method != next_method
            ],
            "attempt_count": len(lesson_results),
            "lesson_completed": False,
        }

    return {
        "recommended_method": "quiz",
        "title": "Retake the Quiz",
        "reason": "You have already attempted every available learning method. Please retake the quiz when ready.",
        "used_methods": used_methods,
        "remaining_methods": [],
        "attempt_count": len(lesson_results),
        "lesson_completed": False,
    }


def get_current_learning_method(lesson_id, user_id, role):
    lesson, error = _get_visible_lesson(lesson_id, role)
    if error:
        return None, error

    profile = adaptive_learning_service.get_learning_profile(user_id)
    lesson_results = adaptive_learning_service.get_learning_method_results(
        user_id,
        lesson.id,
    )
    recommendation = _build_recommendation_payload(
        lesson,
        user_id,
        profile,
        lesson_results,
    )

    return recommendation["recommended_method"], None


def get_lesson_recommendation(lesson_id, user_id, role):
    lesson, error = _get_visible_lesson(lesson_id, role)
    if error:
        return error

    profile = adaptive_learning_service.get_learning_profile(user_id)
    lesson_results = adaptive_learning_service.get_learning_method_results(
        user_id,
        lesson.id,
    )
    recommendation = _build_recommendation_payload(
        lesson,
        user_id,
        profile,
        lesson_results,
    )

    return _success(
        "Recommendation retrieved successfully",
        {
            "recommendation": recommendation,
            "profile": adaptive_learning_service.serialize_learning_profile(profile),
            "history": [
                adaptive_learning_service.serialize_learning_method_result(result)
                for result in lesson_results
            ],
        }
    )


def advance_learning_stage(lesson_id, user_id, role):
    # Kept for compatibility with older frontend calls.
    return get_lesson_recommendation(lesson_id, user_id, role)


def sync_progress_after_quiz_attempt(lesson_id, user_id, passed, next_method):
    progress = Progress.query.filter_by(
        lesson_id=lesson_id,
        user_id=int(user_id),
    ).first()

    if not progress:
        progress = Progress(
            lesson_id=lesson_id,
            user_id=int(user_id),
        )
        db.session.add(progress)

    if passed:
        progress.status = "completed"
        progress.completion_percentage = 100
        progress.current_learning_stage = "completed"
        progress.completed_at = datetime.utcnow()
    else:
        progress.status = "in_progress"
        progress.completion_percentage = max(progress.completion_percentage, 50)
        progress.current_learning_stage = next_method or "material"
        progress.completed_at = None

    progress.last_accessed_at = datetime.utcnow()
    db.session.flush()
    return progress


def _get_learning_method_title(learning_method):
    titles = {
        "material": "Study the Original Learning Material",
        "summary": "Study the AI Summary",
        "mind_map": "Study the AI Mind Map",
    }
    return titles.get(learning_method, "Continue Learning")


def _build_method_reason(
    learning_method,
    profile,
    method_metrics,
    is_first_attempt=False,
    previous_result=None,
):
    if is_first_attempt and not adaptive_learning_service.has_historical_data(profile):
        if learning_method == "material":
            return (
                "This is your first lesson, therefore the system recommends "
                "beginning with the original learning material."
            )

        return (
            "This is your first lesson, so the system is starting with the "
            "best available learning method for this lesson."
        )

    metrics = method_metrics.get(learning_method, {})
    average_score = round(float(metrics.get("average_score", 0.0)), 2)
    success_rate = round(float(metrics.get("success_rate", 0.0)), 2)
    total_attempts = int(metrics.get("total_attempts", 0))
    successful_attempts = int(metrics.get("successful_attempts", 0))

    prefix = ""
    if previous_result and not previous_result.passed:
        prefix = "You did not pass the last quiz attempt. "

    if total_attempts <= 0:
        return (
            f"{prefix}This learning method has not been used successfully in your "
            "history yet, so it is being recommended as the strongest remaining "
            "unused option for this lesson."
        )

    best_average_method = _get_best_method_by("average_score", method_metrics)
    best_success_method = _get_best_method_by("success_rate", method_metrics)

    if learning_method == "summary":
        if best_average_method == "summary":
            return (
                f"{prefix}Based on your previous quiz performance, AI summaries "
                f"have produced your highest average quiz score at "
                f"{average_score}% with a {success_rate}% success rate across "
                f"{total_attempts} attempt(s)."
            )

        return (
            f"{prefix}Based on your previous quiz performance, AI summaries are "
            f"one of your strongest learning methods, with an average quiz score "
            f"of {average_score}% and a {success_rate}% success rate."
        )

    if learning_method == "mind_map":
        if best_success_method == "mind_map":
            return (
                f"{prefix}Your previous learning history shows better "
                f"understanding after studying AI mind maps, which currently "
                f"have your highest success rate at {success_rate}%."
            )

        return (
            f"{prefix}Your previous learning history shows better understanding "
            f"after studying AI mind maps, with an average quiz score of "
            f"{average_score}% and {successful_attempts} successful attempt(s)."
        )

    if best_success_method == "material":
        return (
            f"{prefix}Your previous learning history indicates that studying the "
            f"original learning material produces the best results, with a "
            f"{success_rate}% success rate and an average quiz score of "
            f"{average_score}%."
        )

    return (
        f"{prefix}Your previous learning history indicates that studying the "
        f"original learning material remains a strong option, with an average "
        f"quiz score of {average_score}% and a {success_rate}% success rate."
    )


def _get_best_method_by(field_name, method_metrics):
    attempted_methods = [
        method
        for method, metrics in method_metrics.items()
        if int(metrics.get("total_attempts", 0)) > 0
    ]

    if not attempted_methods:
        return None

    ranked_methods = sorted(
        attempted_methods,
        key=lambda method: (
            -float(method_metrics[method].get(field_name, 0.0)),
            -int(method_metrics[method].get("successful_attempts", 0)),
            -int(method_metrics[method].get("total_attempts", 0)),
            adaptive_learning_service.DEFAULT_METHOD_ORDER[method],
        ),
    )
    return ranked_methods[0]
