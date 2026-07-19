import { useState } from 'react';
import { Alert, Box, Button, Card, CardContent, Stack, TextField, Typography } from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth.jsx';
import { getErrorMessage } from '../utils/apiResponse';

export function RegisterPage() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
  });
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
      await register(formData);
      navigate('/login');
    } catch (registerError) {
      setError(getErrorMessage(registerError));
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
          'radial-gradient(circle at top, rgba(19, 50, 79, 0.16), transparent 28%), linear-gradient(180deg, #f8fbff 0%, #eef4fb 100%)',
      }}
    >
      <Card sx={{ width: '100%', maxWidth: 520 }}>
        <CardContent sx={{ p: 4 }}>
          <Stack spacing={2.5} component="form" onSubmit={handleSubmit}>
            <Box>
              <Typography variant="h4" gutterBottom>
                Create account
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Register to access the learning platform.
              </Typography>
            </Box>

            {error ? <Alert severity="error">{error}</Alert> : null}

            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label="First Name"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                required
                fullWidth
              />
              <TextField
                label="Last Name"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                required
                fullWidth
              />
            </Stack>

            <TextField
              label="Username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              fullWidth
            />
            <TextField
              label="Email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              type="email"
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
              {loading ? 'Creating account...' : 'Register'}
            </Button>

            <Typography variant="body2" color="text.secondary">
              Already have an account?{' '}
              <Button component={RouterLink} to="/login" size="small">
                Login
              </Button>
            </Typography>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}
