from adaptive_learning.extensions import db
from adaptive_learning.models.lesson import Lesson
from adaptive_learning.models.lesson_resource import LessonResource
from adaptive_learning.models.progress import Progress
from adaptive_learning.models.quiz_attempt import QuizAttempt
from adaptive_learning.models.student_learning_method_result import (
    StudentLearningMethodResult,
)
from adaptive_learning.models.student_learning_profile import (
    StudentLearningProfile,
)


LEARNING_METHODS = (
    "material",
    "summary",
    "mind_map",
)

DEFAULT_METHOD_ORDER = {
    "material": 0,
    "summary": 1,
    "mind_map": 2,
}


def _empty_method_metrics():
    return {
        "total_attempts": 0,
        "successful_attempts": 0,
        "success_rate": 0.0,
        "average_score": 0.0,
        "usage_count": 0,
        "last_score": None,
        "last_attempted_at": None,
        "_score_total": 0,
    }


def serialize_learning_profile(profile):
    if not profile:
        return {
            "preferred_learning_method": None,
            "total_results": 0,
            "average_quiz_score": 0.0,
            "average_attempts": 0.0,
            "material_success_rate": 0.0,
            "summary_success_rate": 0.0,
            "mindmap_success_rate": 0.0,
            "updated_at": None,
        }

    return {
        "preferred_learning_method": profile.preferred_learning_method,
        "total_results": profile.total_results,
        "average_quiz_score": profile.average_quiz_score,
        "average_attempts": profile.average_attempts,
        "material_success_rate": profile.material_success_rate,
        "summary_success_rate": profile.summary_success_rate,
        "mindmap_success_rate": profile.mindmap_success_rate,
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
    }


def serialize_learning_method_result(result):
    return {
        "id": result.id,
        "student_id": result.student_id,
        "lesson_id": result.lesson_id,
        "learning_method": result.learning_method,
        "quiz_attempt_id": result.quiz_attempt_id,
        "attempt_number": result.attempt_number,
        "score": result.score,
        "passed": result.passed,
        "improvement": result.improvement,
        "created_at": result.created_at.isoformat(),
    }


def get_available_learning_methods(lesson):
    available_methods = []

    if lesson.content or _has_published_resource(lesson.id, "material"):
        available_methods.append("material")

    if lesson.summary or _has_generated_resource(lesson.id, "summary"):
        available_methods.append("summary")

    if _has_generated_resource(lesson.id, "knowledge_graph"):
        available_methods.append("mind_map")

    return available_methods


def get_learning_method_results(student_id, lesson_id):
    return StudentLearningMethodResult.query.filter_by(
        student_id=int(student_id),
        lesson_id=lesson_id,
    ).order_by(
        StudentLearningMethodResult.attempt_number.asc(),
        StudentLearningMethodResult.created_at.asc(),
    ).all()


def has_historical_data(profile):
    return bool(profile and profile.total_results > 0)


def get_learning_method_success_rate(profile, learning_method):
    if not profile:
        return 0.0

    if learning_method == "material":
        return float(profile.material_success_rate or 0.0)
    if learning_method == "summary":
        return float(profile.summary_success_rate or 0.0)
    if learning_method == "mind_map":
        return float(profile.mindmap_success_rate or 0.0)

    return 0.0


def get_learning_method_metrics(student_id):
    results = StudentLearningMethodResult.query.filter_by(
        student_id=int(student_id)
    ).order_by(
        StudentLearningMethodResult.created_at.asc(),
        StudentLearningMethodResult.id.asc(),
    ).all()

    metrics = {
        method: _empty_method_metrics()
        for method in LEARNING_METHODS
    }

    for result in results:
        method_metrics = metrics.get(result.learning_method)
        if method_metrics is None:
            continue

        method_metrics["total_attempts"] += 1
        method_metrics["usage_count"] += 1
        method_metrics["_score_total"] += result.score
        method_metrics["last_score"] = result.score
        method_metrics["last_attempted_at"] = (
            result.created_at.isoformat()
            if result.created_at
            else None
        )

        if result.passed:
            method_metrics["successful_attempts"] += 1

    for method_metrics in metrics.values():
        if method_metrics["total_attempts"] > 0:
            method_metrics["average_score"] = round(
                method_metrics["_score_total"] / method_metrics["total_attempts"],
                2,
            )
            method_metrics["success_rate"] = round(
                (
                    method_metrics["successful_attempts"]
                    / method_metrics["total_attempts"]
                ) * 100,
                2,
            )

        method_metrics.pop("_score_total", None)

    return metrics


def rank_learning_methods(available_methods, student_id=None, metrics=None):
    metrics = metrics or (
        get_learning_method_metrics(student_id)
        if student_id is not None
        else {
            method: _empty_method_metrics()
            for method in LEARNING_METHODS
        }
    )

    return sorted(
        available_methods,
        key=lambda method: (
            -float(metrics[method]["success_rate"]),
            -float(metrics[method]["average_score"]),
            -int(metrics[method]["successful_attempts"]),
            -int(metrics[method]["total_attempts"]),
            -int(metrics[method]["last_score"] or -1),
            DEFAULT_METHOD_ORDER[method],
        ),
    )


def choose_initial_learning_method(lesson, student_id, profile):
    available_methods = get_available_learning_methods(lesson)
    if not available_methods:
        return None

    if not has_historical_data(profile):
        if "material" in available_methods:
            return "material"
        return available_methods[0]

    ranked_methods = rank_learning_methods(
        available_methods,
        student_id=student_id,
    )
    return ranked_methods[0] if ranked_methods else None


def choose_next_learning_method(lesson, student_id, profile, used_methods):
    available_methods = get_available_learning_methods(lesson)
    ranked_methods = rank_learning_methods(
        available_methods,
        student_id=student_id,
    )

    for method in ranked_methods:
        if method not in used_methods:
            return method

    return None


def get_or_create_learning_profile(student_id):
    profile = StudentLearningProfile.query.filter_by(
        student_id=int(student_id)
    ).first()

    if profile:
        return profile

    profile = StudentLearningProfile(student_id=int(student_id))
    db.session.add(profile)
    db.session.flush()
    return profile


def get_learning_profile(student_id):
    return StudentLearningProfile.query.filter_by(
        student_id=int(student_id)
    ).first()


def record_learning_method_result(
    student_id,
    lesson_id,
    learning_method,
    quiz_attempt_id,
    score,
    passed,
):
    previous_results = get_learning_method_results(student_id, lesson_id)
    previous_result = previous_results[-1] if previous_results else None
    attempt_number = len(previous_results) + 1

    result = StudentLearningMethodResult(
        student_id=int(student_id),
        lesson_id=lesson_id,
        learning_method=learning_method,
        quiz_attempt_id=quiz_attempt_id,
        attempt_number=attempt_number,
        score=score,
        passed=passed,
        improvement=(
            score - previous_result.score
            if previous_result
            else None
        ),
    )
    db.session.add(result)
    db.session.flush()

    profile = sync_learning_profile(student_id)

    return result, profile


def sync_learning_profile(student_id):
    profile = get_or_create_learning_profile(student_id)
    results = StudentLearningMethodResult.query.filter_by(
        student_id=int(student_id)
    ).order_by(
        StudentLearningMethodResult.created_at.asc(),
        StudentLearningMethodResult.id.asc(),
    ).all()

    total_results = len(results)
    profile.total_results = total_results

    if not total_results:
        profile.preferred_learning_method = None
        profile.average_quiz_score = 0.0
        profile.average_attempts = 0.0
        profile.material_success_rate = 0.0
        profile.summary_success_rate = 0.0
        profile.mindmap_success_rate = 0.0
        db.session.flush()
        return profile

    profile.average_quiz_score = round(
        sum(result.score for result in results) / total_results,
        2,
    )

    passed_results = [result for result in results if result.passed]
    if passed_results:
        profile.average_attempts = round(
            sum(result.attempt_number for result in passed_results)
            / len(passed_results),
            2,
        )
    else:
        profile.average_attempts = 0.0

    method_metrics = get_learning_method_metrics(student_id)

    profile.material_success_rate = method_metrics["material"]["success_rate"]
    profile.summary_success_rate = method_metrics["summary"]["success_rate"]
    profile.mindmap_success_rate = method_metrics["mind_map"]["success_rate"]

    attempted_methods = [
        method
        for method in LEARNING_METHODS
        if method_metrics[method]["total_attempts"] > 0
    ]

    if attempted_methods:
        profile.preferred_learning_method = rank_learning_methods(
            attempted_methods,
            metrics=method_metrics,
        )[0]
    else:
        profile.preferred_learning_method = None

    db.session.flush()
    return profile


def get_learning_analytics(student_id):
    profile = get_learning_profile(student_id)
    metrics = get_learning_method_metrics(student_id)

    return {
        "preferred_learning_method": (
            profile.preferred_learning_method
            if profile
            else None
        ),
        "average_quiz_score": (
            float(profile.average_quiz_score or 0.0)
            if profile
            else 0.0
        ),
        "average_attempts": (
            float(profile.average_attempts or 0.0)
            if profile
            else 0.0
        ),
        "total_results": int(profile.total_results or 0) if profile else 0,
        "total_lessons_completed": Progress.query.filter_by(
            user_id=int(student_id),
            status="completed",
        ).count(),
        "total_quiz_attempts": QuizAttempt.query.filter_by(
            user_id=int(student_id)
        ).count(),
        "method_metrics": {
            method: {
                "average_score": metrics[method]["average_score"],
                "success_rate": metrics[method]["success_rate"],
                "total_attempts": metrics[method]["total_attempts"],
                "successful_attempts": metrics[method]["successful_attempts"],
                "usage_count": metrics[method]["usage_count"],
            }
            for method in LEARNING_METHODS
        },
    }


def _has_generated_resource(lesson_id, resource_type):
    return LessonResource.query.filter_by(
        lesson_id=lesson_id,
        resource_type=resource_type,
        is_generated=True,
        is_published=True,
    ).first() is not None


def _has_published_resource(lesson_id, resource_type):
    return LessonResource.query.filter_by(
        lesson_id=lesson_id,
        resource_type=resource_type,
        is_published=True,
    ).first() is not None
