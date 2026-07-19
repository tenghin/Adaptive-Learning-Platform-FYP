import { useEffect, useMemo, useState } from 'react';
import { useParams, Link as RouterLink } from 'react-router-dom';
import { Box, Button, Grid, Paper, Stack, Typography, Chip, LinearProgress } from '@mui/material';
import { courseService } from '../services/courseService';
import { progressService } from '../services/progressService';
import { LessonCard } from '../components/LessonCard';
import { getErrorMessage } from '../utils/apiResponse';

export function CourseDetailsPage() {
  const { courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [lessons, setLessons] = useState([]);
  const [courseProgress, setCourseProgress] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadCourse = async () => {
      try {
        const [courseData, lessonsData, progressData] = await Promise.all([
          courseService.getCourse(courseId),
          courseService.listLessons(courseId),
          progressService.getCourseProgress(courseId),
        ]);

        setCourse(courseData.course || null);
        setLessons(lessonsData.lessons || []);
        setCourseProgress(progressData);
      } catch (courseError) {
        setError(getErrorMessage(courseError));
      }
    };

    loadCourse();
  }, [courseId]);

  if (error) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography color="error">{error}</Typography>
      </Paper>
    );
  }

  return (
    <Stack spacing={3}>
      <Button component={RouterLink} to="/courses" variant="text" sx={{ alignSelf: 'flex-start' }}>
        Back to courses
      </Button>

      <Paper sx={{ p: { xs: 3, md: 4 } }}>
        <Stack spacing={1}>
          <Typography variant="overline" color="text.secondary">
            Course Details
          </Typography>
          <Typography variant="h4">{course?.title || 'Loading course...'}</Typography>
          <Typography variant="body1" color="text.secondary">
            {course?.description}
          </Typography>
        </Stack>
      </Paper>

      {courseProgress ? (
        <Paper sx={{ p: { xs: 3, md: 4 } }}>
          <Stack spacing={2}>
            <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
              <Typography variant="h6">Progress</Typography>
              <Chip label={`${courseProgress.summary.overall_completion_percentage}% complete`} color="primary" />
              <Chip label={`${courseProgress.summary.completed_lessons} completed`} color="success" variant="outlined" />
              <Chip label={`${courseProgress.summary.in_progress_lessons} in progress`} color="warning" variant="outlined" />
            </Stack>
            <LinearProgress
              variant="determinate"
              value={courseProgress.summary.overall_completion_percentage}
              sx={{ height: 10, borderRadius: 999 }}
            />
          </Stack>
        </Paper>
      ) : null}

      <Box>
        <Typography variant="h5" gutterBottom>
          Lessons
        </Typography>
        <Grid container spacing={3}>
          {lessons.map((lesson) => {
            const lessonProgress = courseProgress?.lessons?.find(
              (item) => item.lesson.id === lesson.id
            )?.progress;

            console.log("Lesson:", lesson.id);
            console.log("Progress:", lessonProgress);

            return (
            <Grid key={lesson.id} item xs={12} md={6}>
                <LessonCard lesson={lesson} progress={lessonProgress} />
            </Grid>
            );
          })}
        </Grid>
      </Box>
    </Stack>
  );
}
