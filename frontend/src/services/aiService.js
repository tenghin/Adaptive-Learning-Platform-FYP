import { lessonService } from './lessonService';

export const aiService = {
  generateSummary: lessonService.generateSummary,
  generateKnowledgeGraph: lessonService.generateKnowledgeGraph,
};
