import { Navigate, Route, Routes } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { LoadingScreen } from '../components/LoadingScreen';
import { useAuth } from '../hooks/useAuth.jsx';
import { AdminRoute, ProtectedRoute, PublicRoute } from './ProtectedRoute';
import { LoginPage } from '../pages/LoginPage';
import { RegisterPage } from '../pages/RegisterPage';
import { ForgotPasswordPage } from '../pages/ForgotPasswordPage';
import { ResetPasswordPage } from '../pages/ResetPasswordPage';
import { DashboardPage } from '../pages/DashboardPage';
import { CourseListPage } from '../pages/CourseListPage';
import { CourseDetailsPage } from '../pages/CourseDetailsPage';
import { LessonPage } from '../pages/LessonPage';
import { QuizPage } from '../pages/QuizPage';
import { ProfilePage } from '../pages/ProfilePage';
import { AdminManagementPage } from '../pages/AdminManagementPage';
import { NotFoundPage } from '../pages/NotFoundPage';

function AppRoutes() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <Routes>
      <Route
        path="/"
        element={
          <Navigate
            to={isAuthenticated ? '/dashboard' : '/login'}
            replace
          />
        }
      />

      <Route element={<PublicRoute />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/courses" element={<CourseListPage />} />
          <Route path="/courses/:courseId" element={<CourseDetailsPage />} />
          <Route path="/lessons/:lessonId" element={<LessonPage />} />
          <Route path="/lessons/:lessonId/quiz" element={<QuizPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Route>
      </Route>

      <Route element={<AdminRoute />}>
        <Route element={<Layout />}>
          <Route path="/admin" element={<AdminManagementPage />} />
        </Route>
      </Route>

      <Route
        path="*"
        element={
          <Navigate
            to={isAuthenticated ? '/dashboard' : '/login'}
            replace
          />
        }
      />
    </Routes>
  );
}

export default AppRoutes;
