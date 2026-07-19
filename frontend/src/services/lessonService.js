import { api } from './api';
import { unwrapData } from '../utils/apiResponse';

async function getLesson(lessonId) {
  const response = await api.get(`/api/lessons/${lessonId}`);
  return unwrapData(response);
}

async function listLessonResources(lessonId) {
  const response = await api.get(`/api/lessons/${lessonId}/resources`);
  return unwrapData(response);
}

async function generateSummary(lessonId) {
  const response = await api.post(`/api/lessons/${lessonId}/ai/summary`);
  return unwrapData(response);
}

async function generateKnowledgeGraph(lessonId) {
  const response = await api.post(`/api/lessons/${lessonId}/ai/knowledge-graph`);
  return unwrapData(response);
}

async function generateQuiz(lessonId) {
    const response = await api.post(`/api/lessons/${lessonId}/ai/quiz`);
    return unwrapData(response);
}

async function createLesson(courseId, payload) {
  const response = await api.post(`/api/courses/${courseId}/lessons`, payload);
  return unwrapData(response);
}

async function updateLesson(lessonId, payload) {
  const response = await api.put(`/api/lessons/${lessonId}`, payload);
  return unwrapData(response);
}

async function deleteLesson(lessonId) {
  const response = await api.delete(`/api/lessons/${lessonId}`);
  return unwrapData(response);
}

async function downloadLearningMaterial(resourceId) {
    const response = await api.get(
        `/api/lesson-resources/${resourceId}/download`,
        {
            responseType: "blob",
        }
    );

    return response.data;
}

async function uploadLearningMaterial(lessonId, formData) {
    const response = await api.post(
        `/api/lessons/${lessonId}/learning-materials`,
        formData,
        {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        }
    );

    return unwrapData(response);
}

async function deleteLearningMaterial(resourceId) {
    const response = await api.delete(
        `/api/lesson-resources/${resourceId}`
    );

    return unwrapData(response);
}

export const lessonService = {
  getLesson,
  listLessonResources,
  generateSummary,
  generateKnowledgeGraph,
  generateQuiz,
  createLesson,
  updateLesson,
  deleteLesson,
  downloadLearningMaterial,
  uploadLearningMaterial,
  deleteLearningMaterial,
};

