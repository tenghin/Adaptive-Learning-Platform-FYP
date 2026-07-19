import { useState } from 'react';
import { Alert, Box, Button, Card, CardContent, Stack, TextField, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { authService } from '../services/authService';
import { getErrorMessage } from '../utils/apiResponse';

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setMessage('');
    setResetToken('');
    setError('');

    try {
      const responseData = await authService.forgotPassword({ email });
      setMessage(responseData.message || 'Password reset request sent.');
      setResetToken(responseData.reset_token || '');
    } catch (forgotPasswordError) {
      setError(getErrorMessage(forgotPasswordError));
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
          'radial-gradient(circle at top, rgba(18, 50, 79, 0.12), transparent 28%), linear-gradient(180deg, #f8fbff 0%, #eef4fb 100%)',
      }}
    >
      <Card sx={{ width: '100%', maxWidth: 500 }}>
        <CardContent sx={{ p: 4 }}>
          <Stack component="form" spacing={2.5} onSubmit={handleSubmit}>
            <Box>
              <Typography variant="h4" gutterBottom>
                Forgot password
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Enter your email address to request a password reset.
              </Typography>
            </Box>

            {message ? <Alert severity="success">{message}</Alert> : null}
            {error ? <Alert severity="error">{error}</Alert> : null}

            {resetToken ? (
              <Alert severity="info">
                Demo reset token: <strong>{resetToken}</strong>
              </Alert>
            ) : null}

            <TextField
              label="Email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              fullWidth
            />

            <Button type="submit" variant="contained" size="large" disabled={loading}>
              {loading ? 'Sending...' : 'Send reset link'}
            </Button>

            <Typography variant="body2" color="text.secondary">
              Remembered it?{' '}
              <Button component={RouterLink} to="/login" size="small">
                Back to login
              </Button>
            </Typography>

            <Typography variant="body2" color="text.secondary">
              Have a reset token?{' '}
              <Button component={RouterLink} to="/reset-password" size="small">
                Set a new password
              </Button>
            </Typography>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}
