import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams, Link as RouterLink } from 'react-router-dom';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Divider,
  FormControl,
  FormControlLabel,
  FormLabel,
  Paper,
  Radio,
  RadioGroup,
  Stack,
  Typography,
  Chip,
} from '@mui/material';
import { learningActivityService } from '../services/learningActivityService';
import { quizService } from '../services/quizService';
import { getErrorMessage } from '../utils/apiResponse';


function sortQuestions(questions) {
  return [...questions].sort((left, right) => left.order_index - right.order_index);
}


export function QuizPage() {
  const { lessonId } = useParams();
  const navigate = useNavigate();

  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [attemptsLoading, setAttemptsLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [attempts, setAttempts] = useState([]);

  useEffect(() => {
    const loadQuizAndAttempts = async () => {
      try {
        const data = await quizService.getLessonQuiz(lessonId);
        const quizData = data.quiz || null;
        setQuiz(quizData);

        await learningActivityService.recordActivity({
          lesson_id: Number(lessonId),
          activity_type: 'quiz_started',
        });

        if (quizData?.id) {
          const attemptsData = await quizService.getMyQuizAttempts(quizData.id);
          setAttempts(attemptsData.attempts || []);
        } else {
          setAttempts([]);
        }
      } catch (quizError) {
        if (quizError?.response?.status === 404) {
          setQuiz(null);
          setError('No quiz is available for this lesson yet.');
        } else {
          setError(getErrorMessage(quizError));
        }
      } finally {
        setLoading(false);
        setAttemptsLoading(false);
      }
    };

    loadQuizAndAttempts();
  }, [lessonId]);

  const questions = useMemo(() => sortQuestions(quiz?.questions || []), [quiz]);

  const handleSelectAnswer = (questionId, selectedAnswer) => {
    setAnswers((current) => ({
      ...current,
      [questionId]: selectedAnswer,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      const payload = {
        answers: questions.map((question) => ({
          question_id: question.id,
          selected_answer: answers[question.id],
        })),
      };

      const responseData = await quizService.submitQuizAttempt(quiz.id, payload);
      await learningActivityService.recordActivity({
        lesson_id: Number(lessonId),
        activity_type: 'quiz_completed',
      });
      setResult(responseData);

      const attemptsData = await quizService.getMyQuizAttempts(quiz.id);
      setAttempts(attemptsData.attempts || []);
    } catch (submitError) {
      setError(getErrorMessage(submitError));
    } finally {
      setSubmitting(false);
    }
  };

  const handleClearAnswers = () => {
    setAnswers({});
    setError('');
  };

  const handleContinue = () => {
    navigate(`/lessons/${lessonId}`);
  };

  if (loading) {
    return (
      <Paper sx={{ p: 4 }}>
        <Typography>Loading quiz...</Typography>
      </Paper>
    );
  }

  if (!quiz && error) {
    return (
      <Stack spacing={2}>
        <Alert severity="info">{error}</Alert>
        <Button component={RouterLink} to={`/lessons/${lessonId}`} variant="contained" sx={{ alignSelf: 'flex-start' }}>
          Back to lesson
        </Button>
      </Stack>
    );
  }

  return (
    <Stack spacing={3}>
      <Button component={RouterLink} to={`/lessons/${lessonId}`} variant="text" sx={{ alignSelf: 'flex-start' }}>
        Back to lesson
      </Button>

      <Paper sx={{ p: { xs: 3, md: 4 } }}>
        <Stack spacing={1}>
          <Typography variant="overline" color="text.secondary">
            Quiz
          </Typography>
          <Typography variant="h4">{quiz?.title}</Typography>
          <Typography variant="body1" color="text.secondary">
            {quiz?.description}
          </Typography>
        </Stack>
      </Paper>

      {error ? <Alert severity="error">{error}</Alert> : null}

      {result ? (
        <Paper sx={{ p: { xs: 3, md: 4 } }}>
          <Stack spacing={2}>
            <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
              <Typography variant="h5">Attempt Result</Typography>
              <Button variant="contained" onClick={handleContinue}>
                {result.attempt.passed ? 'Continue' : 'Study Recommended Method'}
              </Button>
            </Stack>

            <Stack direction="row" spacing={1} flexWrap="wrap" alignItems="center">
              <Chip
                label={`${result.attempt.score_percentage}%`}
                color={result.attempt.passed ? 'success' : 'warning'}
              />
              <Chip
                label={result.attempt.passed ? 'Passed' : 'Not passed'}
                variant="outlined"
              />
            </Stack>

            {result.learning_method_result ? (
              <Typography variant="body2" color="text.secondary">
                Learning method used: {result.learning_method_result.learning_method.replaceAll('_', ' ')}
              </Typography>
            ) : null}

            {result.recommendation ? (
              <Alert severity={result.attempt.passed ? 'success' : 'info'}>
                <Typography variant="subtitle2">
                  {result.recommendation.title}
                </Typography>
                <Typography variant="body2">
                  {result.recommendation.reason}
                </Typography>
              </Alert>
            ) : null}

            <Divider />

            <Stack spacing={2}>
              {result.results?.question_results?.map((questionResult) => (
                <Card key={questionResult.question_id} variant="outlined">
                  <CardContent>
                    <Stack spacing={1}>
                      <Typography variant="subtitle1" fontWeight={700}>
                        {questionResult.prompt}
                      </Typography>
                      <Typography variant="body2">
                        Your answer: {questionResult.selected_answer}
                      </Typography>
                      <Typography variant="body2">
                        Correct answer: {questionResult.correct_answer}
                      </Typography>
                      <Typography variant="body2" color={questionResult.is_correct ? 'success.main' : 'error.main'}>
                        {questionResult.is_correct ? 'Correct' : 'Incorrect'}
                      </Typography>
                      {questionResult.explanation ? (
                        <Typography variant="body2" color="text.secondary">
                          Explanation: {questionResult.explanation}
                        </Typography>
                      ) : null}
                    </Stack>
                  </CardContent>
                </Card>
              ))}
            </Stack>
          </Stack>
        </Paper>
      ) : (
        <Paper sx={{ p: { xs: 3, md: 4 } }}>
          <Stack component="form" spacing={3} onSubmit={handleSubmit}>
            {questions.map((question, index) => (
              <Card key={question.id} variant="outlined">
                <CardContent>
                  <Stack spacing={2}>
                    <Box>
                      <Typography variant="overline" color="text.secondary">
                        Question {index + 1}
                      </Typography>
                      <Typography variant="h6">{question.prompt}</Typography>
                    </Box>

                    <FormControl>
                      <FormLabel>Choose one answer</FormLabel>
                      <RadioGroup
                        value={answers[question.id] || ''}
                        onChange={(event) => handleSelectAnswer(question.id, event.target.value)}
                      >
                        {question.options.map((option) => (
                          <FormControlLabel
                            key={option}
                            value={option}
                            control={<Radio />}
                            label={option}
                          />
                        ))}
                      </RadioGroup>
                    </FormControl>
                  </Stack>
                </CardContent>
              </Card>
            ))}

            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <Button type="submit" variant="contained" disabled={submitting} sx={{ alignSelf: 'flex-start' }}>
                {submitting ? 'Submitting...' : 'Submit Quiz'}
              </Button>
              <Button variant="text" onClick={handleClearAnswers} sx={{ alignSelf: 'flex-start' }}>
                Clear answers
              </Button>
            </Stack>
          </Stack>
        </Paper>
      )}

      <Paper sx={{ p: { xs: 3, md: 4 } }}>
        <Stack spacing={2}>
          <Typography variant="h5">My Quiz Attempts</Typography>
          {attemptsLoading ? (
            <Typography color="text.secondary">Loading attempts...</Typography>
          ) : attempts.length ? (
            <Stack spacing={2}>
              {attempts.map((attempt) => (
                <Card key={attempt.id} variant="outlined">
                  <CardContent>
                    <Stack spacing={1}>
                      <Stack direction="row" spacing={1} flexWrap="wrap" alignItems="center">
                        <Chip
                          label={`${attempt.score_percentage}%`}
                          color={attempt.passed ? 'success' : 'warning'}
                          size="small"
                        />
                        <Chip
                          label={attempt.passed ? 'Passed' : 'Not passed'}
                          size="small"
                          variant="outlined"
                        />
                      </Stack>
                      <Typography variant="body2" color="text.secondary">
                        Submitted at {new Date(attempt.submitted_at).toLocaleString()}
                      </Typography>
                      <Typography variant="body2">
                        Correct answers: {attempt.correct_answers} / {attempt.total_questions}
                      </Typography>
                    </Stack>
                  </CardContent>
                </Card>
              ))}
            </Stack>
          ) : (
            <Typography color="text.secondary">
              You have not submitted this quiz yet.
            </Typography>
          )}
        </Stack>
      </Paper>
    </Stack>
  );
}
