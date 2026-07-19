import { api } from './api';
import { unwrapData } from '../utils/apiResponse';

async function login(payload) {
  const response = await api.post('/api/auth/login', payload);
  return unwrapData(response);
}

async function register(payload) {
  const response = await api.post('/api/auth/register', payload);
  return unwrapData(response);
}

async function getProfile() {
  const response = await api.get('/api/auth/profile');
  return unwrapData(response);
}

async function changePassword(payload) {
  const response = await api.post('/api/auth/change-password', payload);
  return unwrapData(response);
}

async function forgotPassword(payload) {
  const response = await api.post('/api/auth/forgot-password', payload);
  return unwrapData(response);
}

async function resetPassword(payload) {
  const response = await api.post('/api/auth/reset-password', payload);
  return unwrapData(response);
}

export const authService = {
  login,
  register,
  getProfile,
  changePassword,
  forgotPassword,
  resetPassword,
};
