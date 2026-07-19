const TOKEN_KEY = 'adaptive_learning_jwt';

export function getStoredToken() {
  return window.localStorage.getItem(TOKEN_KEY) || '';
}

export function setStoredToken(token) {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function removeStoredToken() {
  window.localStorage.removeItem(TOKEN_KEY);
}

export function clearStoredToken() {
  removeStoredToken();
  window.dispatchEvent(new Event('adaptive-auth-changed'));
}
