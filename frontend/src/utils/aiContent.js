export function parseGeneratedContent(content) {
  if (!content) {
    return null;
  }

  if (typeof content === 'object') {
    return content;
  }

  try {
    return JSON.parse(content);
  } catch {
    return null;
  }
}
