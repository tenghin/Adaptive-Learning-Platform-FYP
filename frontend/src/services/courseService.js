import { api } from './api';
import { unwrapData } from '../utils/apiResponse';

async function listCourses() {
  const response = await api.get('/api/courses');
  return unwrapData(response);
}

async function getCourse(courseId) {
  const response = await api.get(`/api/courses/${courseId}`);
  return unwrapData(response);
}

async function listLessons(courseId) {
  const response = await api.get(`/api/courses/${courseId}/lessons`);
  return unwrapData(response);
}

async function createCourse(payload) {
  const response = await api.post('/api/courses', payload);
  return unwrapData(response);
}

async function updateCourse(courseId, payload) {
  const response = await api.put(`/api/courses/${courseId}`, payload);
  return unwrapData(response);
}

async function deleteCourse(courseId) {
  const response = await api.delete(`/api/courses/${courseId}`);
  return unwrapData(response);
}



export const courseService = {
  listCourses,
  getCourse,
  listLessons,
  createCourse,
  updateCourse,
  deleteCourse,
};
