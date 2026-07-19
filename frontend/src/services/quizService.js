import { api } from './api';
import { unwrapData } from '../utils/apiResponse';

async function getLessonQuiz(lessonId) {
  const response = await api.get(`/api/lessons/${lessonId}/quiz`);
  return unwrapData(response);
}

async function getQuiz(quizId) {
  const response = await api.get(`/api/quizzes/${quizId}`);
  return unwrapData(response);
}

async function submitQuizAttempt(quizId, payload) {
  const response = await api.post(`/api/quizzes/${quizId}/attempts`, payload);
  return unwrapData(response);
}

async function getMyQuizAttempts(quizId) {
  const response = await api.get(`/api/quizzes/${quizId}/attempts/me`);
  return unwrapData(response);
}

export const quizService = {
  getLessonQuiz,
  getQuiz,
  submitQuizAttempt,
  getMyQuizAttempts,
};
