import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams, Link as RouterLink } from 'react-router-dom';
import {
  Alert,
  Box,
  Button,
  Chip,
  Divider,
  Paper,
  Stack,
  Typography,
} from '@mui/material';
import { useAuth } from '../hooks/useAuth.jsx';
import { aiService } from '../services/aiService';
import { courseService } from '../services/courseService';
import { learningActivityService } from '../services/learningActivityService';
import { lessonService } from '../services/lessonService';
import { progressService } from '../services/progressService';
import { quizService } from '../services/quizService';
import { recommendationService } from '../services/recommendationService';
import { LearningMaterialUploader } from '../components/LearningMaterialUploader';
import { LessonMindMap } from '../components/LessonMindMap';
import { LessonResourcesPanel } from '../components/LessonResourcesPanel';
import { getErrorMessage } from '../utils/apiResponse';
import { parseGeneratedContent } from '../utils/aiContent';
import ReactMarkdown from "react-markdown";


function getGeneratedResource(resources, resourceType) {
  return resources.find((resource) => resource.resource_type === resourceType);
}


const methodLabelMap = {
  material: 'Original Learning Material',
  summary: 'AI Summary',
  mind_map: 'AI Mind Map',
  quiz: 'Quiz Retry',
};


export function LessonPage() {
  const { lessonId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const isAdmin = user?.role === 'admin';

  const [lesson, setLesson] = useState(null);
  const [course, setCourse] = useState(null);
  const [resources, setResources] = useState([]);
  const [progress, setProgress] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [learningProfile, setLearningProfile] = useState(null);
  const [adaptiveHistory, setAdaptiveHistory] = useState([]);
  const [summary, setSummary] = useState('');
  const [knowledgeGraph, setKnowledgeGraph] = useState(null);
  const [quiz, setQuiz] = useState(null);
  const [quizVersions, setQuizVersions] = useState([]);
  const [showUpload, setShowUpload] = useState(false);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [mindMapLoading, setMindMapLoading] = useState(false);
  const [quizLoading, setQuizLoading] = useState(false);

  const materialResources = useMemo(
    () => resources.filter((resource) => resource.resource_type === 'material'),
    [resources]
  );

  const sortedLessons = useMemo(
    () => [...(course?.lessons || [])].sort((left, right) => left.order_index - right.order_index),
    [course]
  );

  const currentLessonIndex = sortedLessons.findIndex(
    (item) => item.id === Number(lessonId)
  );

  const nextLesson =
    currentLessonIndex >= 0
      ? sortedLessons[currentLessonIndex + 1]
      : null;

  const showNextLesson = recommendation?.recommended_method === 'next_lesson';

  const loadLesson = async () => {
    const [
      lessonData,
      resourcesData,
      progressData,
      recommendationData,
      quizData,
    ] = await Promise.all([
      lessonService.getLesson(lessonId),
      lessonService.listLessonResources(lessonId),
      progressService.getLessonProgress(lessonId),
      recommendationService.getRecommendation(lessonId),
      quizService.getLessonQuiz(lessonId).catch((quizError) => {
        if (quizError?.response?.status === 404) {
          return { quiz: null };
        }
        throw quizError;
      }),
    ]);

    const lessonRecord = lessonData.lesson || null;
    const resourceList = resourcesData.resources || [];

    setLesson(lessonRecord);
    setResources(resourceList);
    setProgress(progressData.progress || null);
    setRecommendation(recommendationData.recommendation || null);
    setLearningProfile(recommendationData.profile || null);
    setAdaptiveHistory(recommendationData.history || []);
    setQuiz(quizData.quiz || null);
    setQuizVersions(quizData.quiz_versions || []);

    const courseData = await courseService.getCourse(lessonRecord.course_id);
    const lessonsData = await courseService.listLessons(lessonRecord.course_id);

    setCourse({
      ...(courseData.course || {}),
      lessons: lessonsData.lessons || [],
    });

    const summaryResource = getGeneratedResource(resourceList, 'summary');
    const graphResource = getGeneratedResource(resourceList, 'knowledge_graph');

    setSummary(
      lessonRecord?.summary
        || parseGeneratedContent(summaryResource?.content)?.summary
        || ''
    );
    setKnowledgeGraph(parseGeneratedContent(graphResource?.content));
  };

  useEffect(() => {
    const initializeLesson = async () => {
      try {
        await loadLesson();
        await learningActivityService.recordActivity({
          lesson_id: Number(lessonId),
          activity_type: 'lesson_opened',
        });
      } catch (lessonError) {
        setError(getErrorMessage(lessonError));
      } finally {
        setLoading(false);
      }
    };

    initializeLesson();
  }, [lessonId]);

  useEffect(() => {
    const markLessonInProgress = async () => {
      if (!progress || progress.status !== 'not_started') {
        return;
      }

      try {
        const responseData = await progressService.updateLessonProgress(lessonId, {
          status: 'in_progress',
          completion_percentage: 50,
        });
        setProgress(responseData.progress || null);
      } catch (progressError) {
        setError(getErrorMessage(progressError));
      }
    };

    markLessonInProgress();
  }, [lessonId, progress]);

  const handleGenerateSummary = async () => {
    setSummaryLoading(true);
    setError('');

    try {
      const responseData = await aiService.generateSummary(lessonId);
      setSummary(responseData.lesson?.summary || '');
      await loadLesson();
    } catch (summaryError) {
      setError(getErrorMessage(summaryError));
    } finally {
      setSummaryLoading(false);
    }
  };

  const handleGenerateMindMap = async () => {
    setMindMapLoading(true);
    setError('');

    try {
      const responseData = await aiService.generateKnowledgeGraph(lessonId);
      setKnowledgeGraph(responseData.knowledge_graph || null);
      await loadLesson();
    } catch (mindMapError) {
      setError(getErrorMessage(mindMapError));
    } finally {
      setMindMapLoading(false);
    }
  };

  const handleGenerateQuiz = async () => {
    setQuizLoading(true);
    setError('');

    try {
      await lessonService.generateQuiz(lessonId);
      await loadLesson();
    } catch (quizError) {
      setError(getErrorMessage(quizError));
    } finally {
      setQuizLoading(false);
    }
  };

  const handleResetProgress = async () => {
    try {
        await progressService.resetLessonProgress(lessonId);

        await loadLesson();

    } catch (error) {
        setError(getErrorMessage(error));
    }
  };

  const renderRecommendedContent = () => {
    const recommendedMethod = recommendation?.recommended_method;

    if (recommendedMethod === 'summary') {
      return (
        <Paper sx={{ p: { xs: 3, md: 4 } }}>
          <Stack spacing={2}>
            <Typography variant="h5">AI Summary</Typography>
            <Typography variant="body2" color="text.secondary">
              Focus on the distilled explanation before you move to the quiz.
            </Typography>
            <Box
              sx={{
                  "& p": {
                      mb: 2,
                      lineHeight: 1.8,
                  },
                  "& ul": {
                      pl: 3,
                      mb: 2,
                  },
                  "& li": {
                      mb: 1,
                  },
                  "& strong": {
                      fontWeight: 700,
                  },
              }}
          >
              <ReactMarkdown>
                  {summary || "No summary is available for this lesson yet."}
              </ReactMarkdown>
          </Box>
          </Stack>
        </Paper>
      );
    }

    if (recommendedMethod === 'mind_map') {
      return (
        <Paper sx={{ p: { xs: 3, md: 4 } }}>
          <Stack spacing={2}>
            <Typography variant="h5">AI Mind Map</Typography>
            <Typography variant="body2" color="text.secondary">
              Study the concept relationships before you retake the quiz.
            </Typography>
            <LessonMindMap knowledgeGraph={knowledgeGraph} />
          </Stack>
        </Paper>
      );
    }

    if (recommendedMethod === 'quiz') {
      return (
        <Paper sx={{ p: { xs: 3, md: 4 } }}>
          <Stack spacing={2}>
            <Typography variant="h5">All Learning Methods Used</Typography>
            <Typography variant="body1" color="text.secondary">
              You have already tried every available learning method for this lesson. Retake the quiz when you feel ready.
            </Typography>
          </Stack>
        </Paper>
      );
    }

    return (
      <Paper sx={{ p: { xs: 3, md: 4 } }}>
        <Stack spacing={3}>
          <Box>
            <Typography variant="h5">Original Learning Material</Typography>
            <Typography variant="body2" color="text.secondary">
              Start with the core material for this lesson.
            </Typography>
          </Box>

          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
            {lesson?.content}
          </Typography>

          {materialResources.length ? (
            <>
              <Divider />
              <LessonResourcesPanel
                resources={materialResources}
                isAdmin={isAdmin}
                onDeleted={loadLesson}
              />
            </>
          ) : null}
        </Stack>
      </Paper>
    );
  };

  if (loading) {
    return <Typography>Loading lesson...</Typography>;
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <Stack spacing={3}>
      <Button component={RouterLink} to="/courses" variant="text" sx={{ alignSelf: 'flex-start' }}>
        Back to courses
      </Button>

      <Paper sx={{ p: { xs: 3, md: 4 } }}>
        <Stack spacing={2}>
          <Box>
            <Typography variant="overline" color="text.secondary">
              Adaptive Lesson
            </Typography>
            <Typography variant="h4">{lesson?.title || 'Loading lesson...'}</Typography>
          </Box>

          <Stack direction="row" spacing={1} flexWrap="wrap" alignItems="center">
            <Chip
              label={progress?.status?.replaceAll('_', ' ') || 'not started'}
              color={
                progress?.status === 'completed'
                  ? 'success'
                  : progress?.status === 'in_progress'
                    ? 'warning'
                    : 'default'
              }
            />
            <Chip
              label={`${progress?.completion_percentage || 0}% complete`}
              variant="outlined"
            />
            {recommendation?.recommended_method ? (
              <Chip
                label={methodLabelMap[recommendation.recommended_method] || recommendation.recommended_method}
                color="primary"
                variant="outlined"
              />
            ) : null}
          </Stack>
        </Stack>
      </Paper>

      {!showNextLesson ? renderRecommendedContent() : null}

      {!showNextLesson && recommendation ? (
        <Paper sx={{ p: { xs: 3, md: 4 } }}>
          <Stack spacing={2}>
            <Typography variant="h5">Recommended Next Step</Typography>
            <Typography variant="subtitle1">{recommendation.title}</Typography>
            <Typography variant="body2" color="text.secondary">
              {recommendation.reason}
            </Typography>

            {adaptiveHistory.length ? (
              <Stack direction="row" spacing={1} flexWrap="wrap">
                {adaptiveHistory.map((entry) => (
                  <Chip
                    key={entry.id}
                    label={`Attempt ${entry.attempt_number}: ${methodLabelMap[entry.learning_method] || entry.learning_method} (${entry.score}%)`}
                    size="small"
                    color={entry.passed ? 'success' : 'default'}
                    variant={entry.passed ? 'filled' : 'outlined'}
                  />
                ))}
              </Stack>
            ) : null}

            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <Button
                component={RouterLink}
                to={`/lessons/${lessonId}/quiz`}
                variant="contained"
                disabled={!quiz}
              >
                {quiz ? 'Take Quiz' : 'Quiz Not Available Yet'}
              </Button>
              <Button
                component={RouterLink}
                to={course ? `/courses/${course.id}` : '/courses'}
                variant="text"
              >
                Leave Lesson
              </Button>
            </Stack>
          </Stack>
        </Paper>
      ) : null}

      {showNextLesson ? (
        <Paper sx={{ p: { xs: 3, md: 4 } }}>
          <Stack spacing={2}>
            <Typography variant="h4">Lesson Completed</Typography>
            <Typography variant="body1">
              You passed the quiz and completed this lesson.
            </Typography>
            <Button
              variant="contained"
              disabled={!nextLesson}
              onClick={() => {
                if (nextLesson) {
                  navigate(`/lessons/${nextLesson.id}`);
                }
              }}
              sx={{ alignSelf: 'flex-start' }}
            >
              {nextLesson ? 'Next Lesson' : 'Course Completed'}
            </Button>
          </Stack>
        </Paper>
      ) : null}

      {isAdmin ? (
        <Paper sx={{ p: { xs: 3, md: 4 } }}>
          <Stack spacing={3}>
            <Box>
              <Typography variant="h5">Admin Lesson Tools</Typography>
              <Typography variant="body2" color="text.secondary">
                Generate AI resources and manage materials without changing the student-facing workflow.
              </Typography>
            </Box>

            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} flexWrap="wrap">
              <Button
                variant="outlined"
                onClick={handleGenerateSummary}
                disabled={!lesson || summaryLoading}
              >
                {summaryLoading ? 'Generating summary...' : 'Generate Summary'}
              </Button>

              <Button
                variant="outlined"
                onClick={handleGenerateMindMap}
                disabled={!lesson || mindMapLoading}
              >
                {mindMapLoading ? 'Generating mind map...' : 'Generate Mind Map'}
              </Button>

              <Button
                variant="contained"
                onClick={handleGenerateQuiz}
                disabled={quizLoading}
              >
                {quizLoading ? 'Generating quiz...' : quiz ? 'Regenerate Quiz' : 'Generate Quiz'}
              </Button>

              <Button variant="contained" onClick={() => setShowUpload((previous) => !previous)}>
                {showUpload ? 'Hide Uploader' : 'Upload Learning Material'}
              </Button>

              <Button
                  color="error"
                  variant="outlined"
                  onClick={handleResetProgress}
              >
                  Reset Progress
              </Button>

            </Stack>

            {learningProfile ? (
              <Stack direction="row" spacing={1} flexWrap="wrap">
                <Chip
                  label={`Preferred: ${learningProfile.preferred_learning_method || 'n/a'}`}
                  size="small"
                />
                <Chip
                  label={`Material ${learningProfile.material_success_rate || 0}%`}
                  size="small"
                  variant="outlined"
                />
                <Chip
                  label={`Summary ${learningProfile.summary_success_rate || 0}%`}
                  size="small"
                  variant="outlined"
                />
                <Chip
                  label={`Mind Map ${learningProfile.mindmap_success_rate || 0}%`}
                  size="small"
                  variant="outlined"
                />
              </Stack>
            ) : null}

            {quizVersions.length ? (
              <Stack spacing={1}>
                <Typography variant="subtitle2" color="text.secondary">
                  Quiz Versions
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap">
                  {quizVersions.map((version) => (
                    <Chip
                      key={version.id}
                      label={`Quiz ${version.id}${version.is_active ? ' active' : ' archived'} - ${version.question_count} questions`}
                      size="small"
                      color={version.is_active ? 'primary' : 'default'}
                      variant={version.is_active ? 'filled' : 'outlined'}
                    />
                  ))}
                </Stack>
              </Stack>
            ) : null}

            {showUpload ? (
              <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.50' }}>
                <LearningMaterialUploader
                  lessonId={lessonId}
                  onUploaded={async () => {
                    await loadLesson();
                    setShowUpload(false);
                  }}
                />

                <Button sx={{ mt: 2 }} onClick={() => setShowUpload(false)}>
                  Cancel
                </Button>
              </Paper>
            ) : null}
          </Stack>
        </Paper>
      ) : null}
    </Stack>
  );
}
