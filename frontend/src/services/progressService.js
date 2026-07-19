import { api } from './api';
import { unwrapData } from '../utils/apiResponse';

async function getProgressOverview() {
  const response = await api.get('/api/progress');
  return unwrapData(response);
}

async function getCourseProgress(courseId) {
  const response = await api.get(`/api/progress/courses/${courseId}`);
  return unwrapData(response);
}

async function updateLessonProgress(lessonId, payload) {
  const response = await api.put(`/api/progress/lessons/${lessonId}`, payload);
  return unwrapData(response);
}

async function resetLessonProgress(lessonId) {
  const response = await api.delete(
    `/api/progress/lessons/${lessonId}`
  );

  return unwrapData(response);
}

async function getLessonProgress(lessonId) {
  const response = await api.get(`/api/progress/lessons/${lessonId}`);
  return unwrapData(response);
}

export const progressService = {
  getProgressOverview,
  getCourseProgress,
  getLessonProgress,
  updateLessonProgress,
  resetLessonProgress,
};
