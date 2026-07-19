from adaptive_learning.extensions import db
from adaptive_learning.models.student_learning_activity import (
    StudentLearningActivity,
)


def record_activity(
    student_id,
    lesson_id,
    activity_type,
    duration_seconds=None,
):
    activity = StudentLearningActivity(
        student_id=student_id,
        lesson_id=lesson_id,
        activity_type=activity_type,
        duration_seconds=duration_seconds,
    )

    db.session.add(activity)
    db.session.commit()