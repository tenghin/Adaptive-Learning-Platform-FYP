import { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Chip,
  Grid,
  LinearProgress,
  Paper,
  Stack,
  Typography,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { CourseCard } from '../components/CourseCard';
import { useAuth } from '../hooks/useAuth.jsx';
import { courseService } from '../services/courseService';
import { progressService } from '../services/progressService';
import { recommendationService } from '../services/recommendationService';
import { getErrorMessage } from '../utils/apiResponse';

const methodLabelMap = {
  material: 'Original Material',
  summary: 'AI Summary',
  mind_map: 'AI Mind Map',
  quiz: 'Quiz Retry',
  next_lesson: 'Next Lesson',
};

const statusOrder = {
  in_progress: 0,
  not_started: 1,
  completed: 2,
};

function formatMethodLabel(method) {
  return methodLabelMap[method] || 'Recommended Method';
}

function sortLessonProgress(a, b) {
  const aStatus = statusOrder[a.progress.status] ?? 99;
  const bStatus = statusOrder[b.progress.status] ?? 99;

  if (aStatus !== bStatus) {
    return aStatus - bStatus;
  }

  const aAccessed = a.progress.last_accessed_at
    ? new Date(a.progress.last_accessed_at).getTime()
    : 0;
  const bAccessed = b.progress.last_accessed_at
    ? new Date(b.progress.last_accessed_at).getTime()
    : 0;

  if (aAccessed !== bAccessed) {
    return bAccessed - aAccessed;
  }

  return a.lesson.order_index - b.lesson.order_index;
}

function buildLessonProgress(courseProgressResponses) {
  return courseProgressResponses
    .flatMap((courseProgress) =>
      (courseProgress?.lessons || []).map((item) => ({
        course: courseProgress.course,
        summary: courseProgress.summary,
        lesson: item.lesson,
        progress: item.progress,
      }))
    )
    .sort(sortLessonProgress);
}

function getAdaptiveRecommendationCandidate(lessonProgress) {
  const continueLesson = lessonProgress.find(
    (item) => item.progress.status === 'in_progress'
  );

  if (continueLesson) {
    return continueLesson;
  }

  return (
    lessonProgress.find((item) => item.progress.status === 'not_started') ||
    lessonProgress.find((item) => item.progress.status !== 'completed') ||
    null
  );
}

export function DashboardPage() {
  const { user } = useAuth();
  const [courses, setCourses] = useState([]);
  const [progressOverview, setProgressOverview] = useState([]);
  const [lessonProgress, setLessonProgress] = useState([]);
  const [continueLearning, setContinueLearning] = useState(null);
  const [adaptiveRecommendation, setAdaptiveRecommendation] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboard = async () => {
      setLoading(true);
      setError('');

      try {
        const [courseData, progressData] = await Promise.all([
          courseService.listCourses(),
          progressService.getProgressOverview(),
        ]);

        const loadedCourses = courseData.courses || [];
        const loadedOverview = progressData.courses || [];

        setCourses(loadedCourses);
        setProgressOverview(loadedOverview);

        if (user?.role !== 'student') {
          setLessonProgress([]);
          setContinueLearning(null);
          setAdaptiveRecommendation(null);
          return;
        }

        const courseProgressResponses = await Promise.all(
          loadedCourses.map((course) => progressService.getCourseProgress(course.id))
        );

        const flattenedLessonProgress = buildLessonProgress(courseProgressResponses);
        const continueCandidate =
          
          flattenedLessonProgress.find((item) => item.progress.status === 'in_progress') ||
          null;
        const recommendationCandidate = getAdaptiveRecommendationCandidate(
          flattenedLessonProgress
        );

        const recommendationTargets = [
          continueCandidate?.lesson.id,
          recommendationCandidate?.lesson.id,
        ].filter(Boolean);

        const uniqueRecommendationTargets = [...new Set(recommendationTargets)];
        const recommendationEntries = await Promise.all(
          uniqueRecommendationTargets.map(async (lessonId) => {
            const data = await recommendationService.getRecommendation(lessonId);
            return [lessonId, data.recommendation || null];
          })
        );

        const recommendationsByLessonId = Object.fromEntries(recommendationEntries);

        setLessonProgress(flattenedLessonProgress);
        setContinueLearning(
          continueCandidate
            ? {
                ...continueCandidate,
                recommendation:
                  recommendationsByLessonId[continueCandidate.lesson.id] || null,
              }
            : null
        );
        setAdaptiveRecommendation(
          recommendationCandidate
            ? {
                ...recommendationCandidate,
                recommendation:
                  recommendationsByLessonId[recommendationCandidate.lesson.id] || null,
              }
            : null
        );
      } catch (dashboardError) {
        setError(getErrorMessage(dashboardError));
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, [user?.role]);

  const myCourses = useMemo(() => {
    return progressOverview
      .filter(
        (item) =>
          item.summary.completed_lessons > 0 ||
          item.summary.in_progress_lessons > 0
      )
      .sort((a, b) => {
        const aActive = a.summary.in_progress_lessons > 0 ? 0 : 1;
        const bActive = b.summary.in_progress_lessons > 0 ? 0 : 1;

        if (aActive !== bActive) {
          return aActive - bActive;
        }

        return (
          b.summary.overall_completion_percentage -
          a.summary.overall_completion_percentage
        );
      });
  }, [progressOverview]);

  const availableCourses = useMemo(() => {
    return courses.filter(
      (course) =>
        !myCourses.some(
          (item) => item.course.id === course.id
        )
    )
    .slice(0, 6); // Limit to 6 available courses for display
  }, [courses, myCourses]);


  if (loading) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography>Loading dashboard...</Typography>
      </Paper>
    );
  }

  return (
    <Stack spacing={4}>
      <Paper
        sx={{
          p: { xs: 3, md: 4 },
          background: 'linear-gradient(135deg, #12324f 0%, #1f4d75 100%)',
          color: 'white',
        }}
      >
        <Stack spacing={2}>
          <Typography variant="overline" sx={{ opacity: 0.8 }}>
            Adaptive Learning Platform
          </Typography>
          <Typography variant="h4" sx={{ fontWeight: 800 }}>
            {user?.role === 'student'
              ? 'Your adaptive study plan is ready.'
              : 'Manage courses, lessons, and adaptive content.'}
          </Typography>
          <Typography variant="body1" sx={{ maxWidth: 760, opacity: 0.9 }}>
            {user?.role === 'student'
              ? 'Pick up where you left off, follow the recommended learning method, and let the platform adapt to how you learn best.'
              : 'Review course progress, inspect learning content, and keep the prototype ready for the next student session.'}
          </Typography>
          <Stack direction="row" spacing={2} flexWrap="wrap">
            <Button component={RouterLink} to="/courses" variant="contained" color="secondary">
              Browse Courses
            </Button>
            <Button
              component={RouterLink}
              to="/profile"
              variant="outlined"
              sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.45)' }}
            >
              View Profile
            </Button>
          </Stack>
        </Stack>
      </Paper>

      {error ? <Alert severity="error">{error}</Alert> : null}

      {user?.role === 'student' ? (
        <>
          <Box>
            <Typography variant="h5" gutterBottom>
              Continue Learning
            </Typography>
            <Paper sx={{ p: 3 }}>
              {continueLearning ? (
                <Stack spacing={2}>
                  <Stack direction="row" spacing={1} flexWrap="wrap">
                    <Chip label={continueLearning.course.title} size="small" />
                    <Chip
                      label={formatMethodLabel(
                        continueLearning.recommendation?.recommended_method
                      )}
                      color="primary"
                      size="small"
                    />
                    <Chip
                      label={`${continueLearning.progress.completion_percentage}% complete`}
                      size="small"
                      variant="outlined"
                    />
                  </Stack>
                  <Typography variant="h6">{continueLearning.lesson.title}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {continueLearning.recommendation?.reason ||
                      'Continue with the current lesson and learning method.'}
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={continueLearning.progress.completion_percentage}
                    sx={{ height: 10, borderRadius: 999 }}
                  />
                  <Button
                    component={RouterLink}
                    to={`/lessons/${continueLearning.lesson.id}`}
                    variant="contained"
                    sx={{ alignSelf: 'flex-start' }}
                  >
                    Continue Learning
                  </Button>
                </Stack>
              ) : (
                <Stack spacing={2}>
                  <Typography variant="body1">
                    You do not have a lesson in progress yet.
                  </Typography>
                  <Button
                    component={RouterLink}
                    to="/courses"
                    variant="contained"
                    sx={{ alignSelf: 'flex-start' }}
                  >
                    Start a Course
                  </Button>
                </Stack>
              )}
            </Paper>
          </Box>

          <Box>
            <Typography variant="h5" gutterBottom>
              The engine suggests your next step should be:
            </Typography>
            <Paper sx={{ p: 3 }}>
              {adaptiveRecommendation ? (
                <Stack spacing={2}>
                  <Stack direction="row" spacing={1} flexWrap="wrap">
                    <Chip label={adaptiveRecommendation.course.title} size="small" />
                    <Chip
                      label={formatMethodLabel(
                        adaptiveRecommendation.recommendation?.recommended_method
                      )}
                      color="secondary"
                      size="small"
                    />
                  </Stack>
                  <Typography variant="h6">{adaptiveRecommendation.lesson.title}</Typography>
                  <Typography variant="subtitle2" color="text.secondary">
                    {adaptiveRecommendation.recommendation?.title || 'Recommended next step'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {adaptiveRecommendation.recommendation?.reason ||
                      'The platform is ready to guide your next learning session.'}
                  </Typography>
                  <Button
                    component={RouterLink}
                    to={`/lessons/${adaptiveRecommendation.lesson.id}`}
                    variant="contained"
                    sx={{ alignSelf: 'flex-start' }}
                  >
                    Start Learning
                  </Button>
                </Stack>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Complete a lesson or open a course to receive an adaptive recommendation.
                </Typography>
              )}
            </Paper>
          </Box>

          <Box>
            <Typography variant="h5" gutterBottom>
              My Courses
            </Typography>
            {myCourses.length ? (
              <Grid container spacing={3}>
                {myCourses.map((item) => (
                  <Grid
                      key={item.course.id}
                      item
                      xs={12}
                      md={6}
                  >
                    <Paper sx={{ p: 3, height: "100%" }}>
                      <Stack spacing={2}>
                            <Typography variant="h6">
                                {item.course.title}
                            </Typography>

                            <LinearProgress
                                variant="determinate"
                                value={item.summary.overall_completion_percentage}
                                sx={{
                                    height: 10,
                                    borderRadius: 999,
                                }}
                            />

                            <Typography
                                variant="body2"
                                color="text.secondary"
                            >
                                {item.summary.overall_completion_percentage}% complete
                            </Typography>

                            <Stack
                                direction="row"
                                spacing={1}
                                flexWrap="wrap"
                            >
                                <Chip
                                    label={`${item.summary.completed_lessons} completed`}
                                    size="small"
                                />

                                <Chip
                                    label={`${item.summary.in_progress_lessons} active`}
                                    size="small"
                                    variant="outlined"
                                />
                            </Stack>

                            <Button
                                component={RouterLink}
                                to={`/courses/${item.course.id}`}
                                variant="contained"
                                sx={{ alignSelf: "flex-start" }}
                            >
                                Continue
                            </Button>
                      </Stack>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Paper sx={{ p: 3 }}>
                <Typography variant="body2" color="text.secondary">
                  Your lesson progress will appear here after you start learning.
                </Typography>
              </Paper>
            )}
          </Box>
        </>
      ) : (
        <Box>
          <Typography variant="h5" gutterBottom>
            My Courses
          </Typography>
          <Grid container spacing={3}>
            {myCourses.slice(0, 3).map((item) => (
              <Grid key={item.course.id} item xs={12} md={4}>
                <Paper sx={{ p: 3, height: "100%" }}>
                    <Stack spacing={2}>

                        <Typography variant="h6">
                            {item.course.title}
                        </Typography>

                        <LinearProgress
                            variant="determinate"
                            value={item.summary.overall_completion_percentage}
                        />

                        <Typography variant="body2">
                            {item.summary.overall_completion_percentage}% complete
                        </Typography>

                        <Stack direction="row" spacing={1}>
                            <Chip
                                label={`${item.summary.completed_lessons} completed`}
                            />

                            <Chip
                                label={`${item.summary.in_progress_lessons} active`}
                            />
                        </Stack>

                        <Button
                            component={RouterLink}
                            to={`/courses/${item.course.id}`}
                            variant="contained"
                            sx={{ alignSelf: "flex-start" }}
                        >
                            Continue
                        </Button>

                    </Stack>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      <Box>
        <Typography variant="h5" gutterBottom>
          Available Courses
        </Typography>
        <Grid container spacing={3}>
          {availableCourses.map((course) => (
            <Grid key={course.id} item xs={12} md={4}>
              <CourseCard course={course} />
            </Grid>
          ))}
        </Grid>
      </Box>
      

    </Stack>
  );
}
