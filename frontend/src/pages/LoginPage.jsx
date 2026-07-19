import { useState } from 'react';
import { Alert, Box, Button, Card, CardContent, Stack, TextField, Typography } from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth.jsx';
import { getErrorMessage } from '../utils/apiResponse';

export function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [formData, setFormData] = useState({ identifier: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');

    try {
      await login(formData);
      navigate('/dashboard');
    } catch (loginError) {
      setError(getErrorMessage(loginError));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'grid',
        placeItems: 'center',
        px: 2,
        background:
          'radial-gradient(circle at top, rgba(224, 159, 62, 0.18), transparent 28%), linear-gradient(180deg, #f8fbff 0%, #eef4fb 100%)',
      }}
    >
      <Card sx={{ width: '100%', maxWidth: 460 }}>
        <CardContent sx={{ p: 4 }}>
          <Stack spacing={2.5} component="form" onSubmit={handleSubmit}>
            <Box>
              <Typography variant="h4" gutterBottom>
                Welcome back
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Sign in to continue learning.
              </Typography>
            </Box>

            {error ? <Alert severity="error">{error}</Alert> : null}

            <TextField
              label="Email or Username"
              name="identifier"
              value={formData.identifier}
              onChange={handleChange}
              required
              fullWidth
            />
            <TextField
              label="Password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              type="password"
              fullWidth
            />

            <Button type="submit" variant="contained" size="large" disabled={loading}>
              {loading ? 'Signing in...' : 'Login'}
            </Button>

            <Typography variant="body2" color="text.secondary">
              Need an account?{' '}
              <Button component={RouterLink} to="/register" size="small">
                Register
              </Button>
            </Typography>

            <Typography variant="body2" color="text.secondary">
              Forgot your password?{' '}
              <Button component={RouterLink} to="/forgot-password" size="small">
                Reset it here
              </Button>
            </Typography>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}
