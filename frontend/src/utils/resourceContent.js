import { parseGeneratedContent } from './aiContent';

export function formatLessonResourceContent(resource) {
  if (!resource) {
    return '';
  }

  if (resource.resource_type === 'summary') {
    const parsedContent = parseGeneratedContent(resource.content);
    return parsedContent?.summary || resource.content || '';
  }

  if (resource.resource_type === 'knowledge_graph') {
    const parsedContent = parseGeneratedContent(resource.content);
    return parsedContent ? 'Knowledge graph generated successfully.' : resource.content || '';
  }

  return resource.content || '';
}
