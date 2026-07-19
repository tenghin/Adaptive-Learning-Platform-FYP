import { Navigate, Outlet } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import { useAuth } from '../hooks/useAuth.jsx';

function LoadingFallback() {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'grid',
        placeItems: 'center',
      }}
    >
      <CircularProgress />
    </Box>
  );
}

export function ProtectedRoute() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <LoadingFallback />;
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
}

export function PublicRoute() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <LoadingFallback />;
  }

  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <Outlet />;
}

export function AdminRoute() {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) {
    return <LoadingFallback />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return user?.role === 'admin' ? <Outlet /> : <Navigate to="/dashboard" replace />;
}
