from adaptive_learning.extensions import db
from adaptive_learning.models.lesson import Lesson
from adaptive_learning.models.question import Question
from adaptive_learning.models.quiz import Quiz
from adaptive_learning.models.quiz_attempt import QuizAttempt
from adaptive_learning.ai.gemini_client import generate_quiz_payload
from adaptive_learning.ai.document_reader import extract_text
from adaptive_learning.models.lesson_resource import LessonResource
from adaptive_learning.models.progress import Progress
from adaptive_learning.services import adaptive_learning_service
from adaptive_learning.services import recommendation_service

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


def _serialize_question(question, include_answer=False):
    payload = {
        "id": question.id,
        "prompt": question.prompt,
        "options": question.options,
        "order_index": question.order_index
    }

    if include_answer:
        payload["correct_answer"] = question.correct_answer
        payload["explanation"] = question.explanation

    return payload


def _serialize_quiz(quiz, include_answers=False):
    return {
        "id": quiz.id,
        "lesson_id": quiz.lesson_id,
        "title": quiz.title,
        "description": quiz.description,
        "pass_percentage": quiz.pass_percentage,
        "is_published": quiz.is_published,
        "is_active": quiz.is_active,
        "created_at": quiz.created_at.isoformat(),
        "updated_at": quiz.updated_at.isoformat(),
        "questions": [
            _serialize_question(question, include_answers)
            for question in quiz.questions
        ]
    }


def _serialize_quiz_version(quiz):
    return {
        "id": quiz.id,
        "lesson_id": quiz.lesson_id,
        "title": quiz.title,
        "is_published": quiz.is_published,
        "is_active": quiz.is_active,
        "question_count": len(quiz.questions),
        "created_at": quiz.created_at.isoformat(),
        "updated_at": quiz.updated_at.isoformat(),
    }


def _serialize_attempt(attempt):
    return {
        "id": attempt.id,
        "quiz_id": attempt.quiz_id,
        "user_id": attempt.user_id,
        "answers": attempt.answers,
        "total_questions": attempt.total_questions,
        "correct_answers": attempt.correct_answers,
        "score_percentage": attempt.score_percentage,
        "passed": attempt.passed,
        "submitted_at": attempt.submitted_at.isoformat()
    }


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


def _get_visible_quiz(quiz_id, role):
    quiz = db.session.get(Quiz, quiz_id)

    if not quiz:
        return None, _failure("Quiz not found", 404)

    if role != "admin" and (
        not quiz.is_active
        or not quiz.is_published
        or not quiz.lesson.is_published
        or not quiz.lesson.course.is_published
    ):
        return None, _failure("Quiz not found", 404)

    return quiz, None


def _get_active_quiz_for_lesson(lesson):
    return lesson.active_quiz


def _get_lesson_quizzes(lesson):
    return sorted(
        lesson.quizzes,
        key=lambda quiz: (
            not quiz.is_active,
            -quiz.id,
        ),
    )


def _deactivate_other_quizzes(lesson, active_quiz_id=None):
    for lesson_quiz in lesson.quizzes:
        lesson_quiz.is_active = lesson_quiz.id == active_quiz_id


def _activate_quiz(quiz):
    for lesson_quiz in quiz.lesson.quizzes:
        lesson_quiz.is_active = lesson_quiz.id == quiz.id


def _get_visible_historical_quiz(quiz_id, role):
    quiz = db.session.get(Quiz, quiz_id)

    if not quiz:
        return None, _failure("Quiz not found", 404)

    if role != "admin" and (
        not quiz.is_published
        or not quiz.lesson.is_published
        or not quiz.lesson.course.is_published
    ):
        return None, _failure("Quiz not found", 404)

    return quiz, None

def _get_lesson_text(lesson):
    lesson_text = lesson.content

    material = LessonResource.query.filter_by(
        lesson_id=lesson.id,
        resource_type="material"
    ).first()

    if material:
        lesson_text = extract_text(material.file_path)

    return lesson_text

def _validate_question_payload(question_data, index):
    if not isinstance(question_data, dict):
        return _failure(
            f"Question {index} must be an object"
        )

    prompt = str(question_data.get("prompt", "")).strip()
    options = question_data.get("options")
    correct_answer = str(
        question_data.get("correct_answer", "")
    ).strip()
    explanation = question_data.get("explanation")
    order_index = question_data.get("order_index", index)

    if not prompt:
        return _failure(f"Question {index} prompt is required")

    if not isinstance(options, list) or len(options) < 2:
        return _failure(
            f"Question {index} must have at least 2 options"
        )

    normalized_options = []
    for option in options:
        option_text = str(option).strip()
        if not option_text:
            return _failure(
                f"Question {index} options cannot be empty"
            )
        normalized_options.append(option_text)

    if correct_answer not in normalized_options:
        return _failure(
            f"Question {index} correct_answer must match one of the options"
        )

    try:
        order_index = int(order_index)
    except (TypeError, ValueError):
        return _failure(
            f"Question {index} order_index must be a valid integer"
        )

    if order_index <= 0:
        return _failure(
            f"Question {index} order_index must be greater than zero"
        )

    explanation = (
        str(explanation).strip()
        if explanation is not None
        else None
    )
    if explanation == "":
        explanation = None

    return {
        "prompt": prompt,
        "options": normalized_options,
        "correct_answer": correct_answer,
        "explanation": explanation,
        "order_index": order_index
    }, 200


def _validate_quiz_payload(data, partial=False):
    data = data or {}

    if partial and not data:
        return _failure("At least one field is required to update a quiz")

    title = str(data.get("title", "")).strip()
    description = data.get("description")
    pass_percentage = data.get("pass_percentage")
    is_published = data.get("is_published")
    is_active = data.get("is_active")
    questions = data.get("questions")

    if not partial and not title:
        return _failure("Quiz title is required")

    if "title" in data and not title:
        return _failure("Quiz title is required")

    if description is not None:
        description = str(description).strip() or None

    if pass_percentage is None:
        if not partial:
            pass_percentage = 70
    else:
        try:
            pass_percentage = int(pass_percentage)
        except (TypeError, ValueError):
            return _failure("pass_percentage must be a valid integer")

        if pass_percentage < 0 or pass_percentage > 100:
            return _failure("pass_percentage must be between 0 and 100")

    if is_published is None:
        if not partial:
            is_published = True
    elif not isinstance(is_published, bool):
        return _failure("is_published must be true or false")

    if is_active is None:
        if not partial:
            is_active = True
    elif not isinstance(is_active, bool):
        return _failure("is_active must be true or false")

    normalized_questions = None
    if questions is not None:
        if not isinstance(questions, list) or not questions:
            return _failure("questions must contain at least one question")

        normalized_questions = []
        for index, question_data in enumerate(questions, start=1):
            validation_result, status_code = _validate_question_payload(
                question_data,
                index
            )
            if status_code != 200:
                return validation_result, status_code
            normalized_questions.append(validation_result)
    elif not partial:
        return _failure("questions must contain at least one question")

    return {
        "title": title,
        "description": description,
        "pass_percentage": pass_percentage,
        "is_published": is_published,
        "is_active": is_active,
        "questions": normalized_questions
    }, 200


def _replace_questions(quiz, questions):
    quiz.questions.clear()

    for question_data in questions:
        quiz.questions.append(
            Question(
                prompt=question_data["prompt"],
                options=question_data["options"],
                correct_answer=question_data["correct_answer"],
                explanation=question_data["explanation"],
                order_index=question_data["order_index"]
            )
        )


def get_lesson_quiz(lesson_id, role):
    lesson, error = _get_visible_lesson(lesson_id, role)
    if error:
        return error

    quiz = _get_active_quiz_for_lesson(lesson)
    if role == "admin" and not quiz and lesson.quizzes:
        quiz = _get_lesson_quizzes(lesson)[0]
    if not quiz:
        return _failure("Quiz not found", 404)

    return _success(
        "Quiz retrieved successfully",
        {
            "quiz": _serialize_quiz(
                quiz,
                include_answers=(role == "admin")
            ),
            "quiz_versions": (
                [_serialize_quiz_version(item) for item in _get_lesson_quizzes(lesson)]
                if role == "admin"
                else []
            )
        }
    )


def get_quiz(quiz_id, role):
    if role == "admin":
        quiz, error = _get_visible_historical_quiz(quiz_id, role)
    else:
        quiz, error = _get_visible_quiz(quiz_id, role)

    if error:
        return error

    return _success(
        "Quiz retrieved successfully",
        {
            "quiz": _serialize_quiz(
                quiz,
                include_answers=(role == "admin")
            )
        }
    )


def create_lesson_quiz(lesson_id, data, role):
    admin_error = _validate_admin(role)
    if admin_error:
        return admin_error

    lesson = db.session.get(Lesson, lesson_id)
    if not lesson:
        return _failure("Lesson not found", 404)

    # Generate quiz using Gemini
    lesson_text = _get_lesson_text(lesson)

    payload, generation_error = generate_quiz_payload(
        lesson.title,
        lesson_text
    )

    if generation_error:
        return _failure(generation_error, 502)

    # Reuse the existing validator
    validation_result, status_code = _validate_quiz_payload(payload)

    if status_code != 200:
        return validation_result, status_code

    quiz = Quiz(
        lesson_id=lesson.id,
        title=validation_result["title"],
        description=validation_result["description"],
        pass_percentage=validation_result["pass_percentage"],
        is_published=validation_result["is_published"],
        is_active=True,
    )

    _deactivate_other_quizzes(lesson)

    _replace_questions(
        quiz,
        validation_result["questions"]
    )

    db.session.add(quiz)
    db.session.commit()

    return _success(
        "Quiz generated successfully",
        {
            "quiz": _serialize_quiz(
                quiz,
                include_answers=True
            ),
            "generation_source": "gemini"
        },
        201
    )


def update_quiz(quiz_id, data, role):
    data = data or {}

    admin_error = _validate_admin(role)
    if admin_error:
        return admin_error

    quiz = db.session.get(Quiz, quiz_id)
    if not quiz:
        return _failure("Quiz not found", 404)

    validation_result, status_code = _validate_quiz_payload(
        data,
        partial=True
    )
    if status_code != 200:
        return validation_result, status_code

    if "title" in data:
        quiz.title = validation_result["title"]

    if "description" in data:
        quiz.description = validation_result["description"]

    if "pass_percentage" in data:
        quiz.pass_percentage = validation_result["pass_percentage"]

    if "is_published" in data:
        quiz.is_published = validation_result["is_published"]

    if "is_active" in data:
        quiz.is_active = validation_result["is_active"]
        if quiz.is_active:
            _activate_quiz(quiz)

    if "questions" in data:
        _replace_questions(quiz, validation_result["questions"])

    db.session.commit()

    return _success(
        "Quiz updated successfully",
        {"quiz": _serialize_quiz(quiz, include_answers=True)}
    )


def delete_quiz(quiz_id, role):
    admin_error = _validate_admin(role)
    if admin_error:
        return admin_error

    quiz = db.session.get(Quiz, quiz_id)
    if not quiz:
        return _failure("Quiz not found", 404)

    quiz.is_active = False
    quiz.is_published = False
    db.session.commit()

    return _success("Quiz archived successfully")


def submit_quiz_attempt(quiz_id, user_id, role, data):
    quiz, error = _get_visible_quiz(quiz_id, role)
    if error:
        return error

    learning_method, recommendation_error = (
        recommendation_service.get_current_learning_method(
            quiz.lesson_id,
            user_id,
            role,
        )
    )
    if recommendation_error:
        return recommendation_error

    if learning_method not in adaptive_learning_service.LEARNING_METHODS:
        previous_results = adaptive_learning_service.get_learning_method_results(
            user_id,
            quiz.lesson_id,
        )
        if previous_results:
            learning_method = previous_results[-1].learning_method
        else:
            learning_method = "material"

    data = data or {}
    answers = data.get("answers")

    if not isinstance(answers, list):
        return _failure("answers must be a list")

    question_map = {question.id: question for question in quiz.questions}
    if not question_map:
        return _failure("Quiz has no questions", 400)

    normalized_answers = []
    answers_by_question_id = {}

    for answer_item in answers:
        if not isinstance(answer_item, dict):
            return _failure("Each answer must be an object")

        question_id = answer_item.get("question_id")
        selected_answer = str(
            answer_item.get("selected_answer", "")
        ).strip()

        try:
            question_id = int(question_id)
        except (TypeError, ValueError):
            return _failure("question_id must be a valid integer")

        question = question_map.get(question_id)
        if not question:
            return _failure("One or more answers reference an invalid question")

        if question_id in answers_by_question_id:
            return _failure("Each question can only be answered once")

        if selected_answer not in question.options:
            return _failure(
                "Selected answer must match one of the question options"
            )

        answers_by_question_id[question_id] = selected_answer
        normalized_answers.append(
            {
                "question_id": question_id,
                "selected_answer": selected_answer
            }
        )

    if len(answers_by_question_id) != len(question_map):
        return _failure("All quiz questions must be answered")

    total_questions = len(quiz.questions)
    correct_answers = 0
    question_results = []

    for question in quiz.questions:
        selected_answer = answers_by_question_id.get(question.id)
        is_correct = selected_answer == question.correct_answer
        if is_correct:
            correct_answers += 1

        question_results.append(
            {
                "question_id": question.id,
                "prompt": question.prompt,
                "selected_answer": selected_answer,
                "correct_answer": question.correct_answer,
                "is_correct": is_correct,
                "explanation": question.explanation
            }
        )

    score_percentage = round((correct_answers / total_questions) * 100)
    passed = score_percentage >= quiz.pass_percentage

    attempt = QuizAttempt(
        quiz_id=quiz.id,
        user_id=int(user_id),
        answers=normalized_answers,
        total_questions=total_questions,
        correct_answers=correct_answers,
        score_percentage=score_percentage,
        passed=passed
    )

    db.session.add(attempt)
    db.session.flush()

    adaptive_result, learning_profile = (
        adaptive_learning_service.record_learning_method_result(
            student_id=user_id,
            lesson_id=quiz.lesson_id,
            learning_method=learning_method,
            quiz_attempt_id=attempt.id,
            score=score_percentage,
            passed=passed,
        )
    )

    latest_recommendation_response, _ = (
        recommendation_service.get_lesson_recommendation(
            quiz.lesson_id,
            user_id,
            role,
        )
    )
    latest_recommendation = latest_recommendation_response["data"][
        "recommendation"
    ]

    recommendation_service.sync_progress_after_quiz_attempt(
        lesson_id=quiz.lesson_id,
        user_id=user_id,
        passed=passed,
        next_method=latest_recommendation.get("recommended_method"),
    )

    db.session.commit()

    return _success(
        "Quiz submitted successfully",
        {
            "attempt": _serialize_attempt(attempt),
            "learning_method_result": (
                adaptive_learning_service.serialize_learning_method_result(
                    adaptive_result
                )
            ),
            "profile": (
                adaptive_learning_service.serialize_learning_profile(
                    learning_profile
                )
            ),
            "recommendation": latest_recommendation,
            "results": {
                "pass_percentage": quiz.pass_percentage,
                "question_results": question_results
            }
        },
        201
    )


def get_my_quiz_attempts(quiz_id, user_id, role):
    quiz, error = _get_visible_historical_quiz(quiz_id, role)
    if error:
        return error

    attempts = QuizAttempt.query.filter_by(
        quiz_id=quiz.id,
        user_id=int(user_id)
    ).order_by(QuizAttempt.submitted_at.desc()).all()

    return _success(
        "Quiz attempts retrieved successfully",
        {"attempts": [_serialize_attempt(attempt) for attempt in attempts]}
    )


def list_quiz_attempts(quiz_id, role):
    admin_error = _validate_admin(role)
    if admin_error:
        return admin_error

    quiz = db.session.get(Quiz, quiz_id)
    if not quiz:
        return _failure("Quiz not found", 404)

    attempts = QuizAttempt.query.filter_by(
        quiz_id=quiz.id
    ).order_by(QuizAttempt.submitted_at.desc()).all()

    return _success(
        "Quiz attempts retrieved successfully",
        {"attempts": [_serialize_attempt(attempt) for attempt in attempts]}
    )
