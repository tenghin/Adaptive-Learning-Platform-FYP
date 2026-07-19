import { api } from './api';
import { unwrapData } from '../utils/apiResponse';

async function getRecommendation(lessonId) {
  const response = await api.get(
    `/api/lessons/${lessonId}/recommendation`
  );

  return unwrapData(response);
}

async function advanceRecommendation(lessonId) {
    const response = await api.post(
        `/api/lessons/${lessonId}/recommendation/advance`
    );

    return unwrapData(response);
}

export const recommendationService = {
  getRecommendation,
  advanceRecommendation,
};