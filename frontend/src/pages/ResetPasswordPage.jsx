import { useState } from 'react';
import { Alert, Box, Button, Card, CardContent, Stack, TextField, Typography } from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
import { getErrorMessage } from '../utils/apiResponse';

export function ResetPasswordPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ token: '', new_password: '' });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setMessage('');
    setError('');

    try {
      const responseData = await authService.resetPassword(formData);
      setMessage(responseData.message || 'Password reset successfully.');
      setTimeout(() => navigate('/login'), 1000);
    } catch (resetPasswordError) {
      setError(getErrorMessage(resetPasswordError));
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((current) => ({ ...current, [name]: value }));
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'grid',
        placeItems: 'center',
        px: 2,
        background:
          'radial-gradient(circle at top, rgba(224, 159, 62, 0.14), transparent 28%), linear-gradient(180deg, #f8fbff 0%, #eef4fb 100%)',
      }}
    >
      <Card sx={{ width: '100%', maxWidth: 500 }}>
        <CardContent sx={{ p: 4 }}>
          <Stack component="form" spacing={2.5} onSubmit={handleSubmit}>
            <Box>
              <Typography variant="h4" gutterBottom>
                Reset password
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Enter the reset token and your new password.
              </Typography>
            </Box>

            {message ? <Alert severity="success">{message}</Alert> : null}
            {error ? <Alert severity="error">{error}</Alert> : null}

            <TextField
              label="Reset Token"
              name="token"
              value={formData.token}
              onChange={handleChange}
              required
              fullWidth
            />
            <TextField
              label="New Password"
              name="new_password"
              type="password"
              value={formData.new_password}
              onChange={handleChange}
              required
              fullWidth
            />

            <Button type="submit" variant="contained" size="large" disabled={loading}>
              {loading ? 'Resetting...' : 'Reset password'}
            </Button>

            <Typography variant="body2" color="text.secondary">
              Back to{' '}
              <Button component={RouterLink} to="/login" size="small">
                login
              </Button>
            </Typography>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}
