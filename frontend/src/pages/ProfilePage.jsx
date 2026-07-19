import { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Chip,
  Grid,
  Paper,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useAuth } from '../hooks/useAuth.jsx';
import { authService } from '../services/authService';
import { getErrorMessage } from '../utils/apiResponse';

const methodLabelMap = {
  material: 'Original Material',
  summary: 'AI Summary',
  mind_map: 'AI Mind Map',
};

function formatMethodLabel(method) {
  return methodLabelMap[method] || 'Not available yet';
}

export function ProfilePage() {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    current_password: '',
    new_password: '',
  });
  const [learningProfile, setLearningProfile] = useState(null);
  const [learningAnalytics, setLearningAnalytics] = useState(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [profileError, setProfileError] = useState('');
  const [loading, setLoading] = useState(false);
  const [profileLoading, setProfileLoading] = useState(true);

  useEffect(() => {
    const loadProfile = async () => {
      setProfileLoading(true);
      setProfileError('');

      try {
        const responseData = await authService.getProfile();
        setLearningProfile(responseData.learning_profile || null);
        setLearningAnalytics(responseData.learning_analytics || null);
      } catch (loadError) {
        setProfileError(getErrorMessage(loadError));
      } finally {
        setProfileLoading(false);
      }
    };

    loadProfile();
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    try {
      const responseData = await authService.changePassword(formData);
      setMessage(responseData.message || 'Password changed successfully.');
      setFormData({ current_password: '', new_password: '' });
    } catch (changePasswordError) {
      setError(getErrorMessage(changePasswordError));
    } finally {
      setLoading(false);
    }
  };

  const methodMetrics = learningAnalytics?.method_metrics || {};

  return (
    <Stack spacing={3}>
      <Paper sx={{ p: { xs: 3, md: 4 } }}>
        <Stack spacing={2}>
          <Typography variant="h4">Profile</Typography>
          <Typography variant="body1" color="text.secondary">
            View your account details, track adaptive learning performance, and update your password.
          </Typography>
          <Stack spacing={1}>
            <Typography variant="body1">
              <strong>Name:</strong> {user?.first_name} {user?.last_name}
            </Typography>
            <Typography variant="body1">
              <strong>Username:</strong> {user?.username}
            </Typography>
            <Typography variant="body1">
              <strong>Email:</strong> {user?.email}
            </Typography>
            <Typography variant="body1">
              <strong>Role:</strong> {user?.role}
            </Typography>
          </Stack>
        </Stack>
      </Paper>

      <Paper sx={{ p: { xs: 3, md: 4 } }}>
        <Stack spacing={3}>
          <Stack spacing={1}>
            <Typography variant="h5">Adaptive Learning Analytics</Typography>
            <Typography variant="body2" color="text.secondary">
              These statistics are generated from your saved adaptive learning history and quiz performance.
            </Typography>
          </Stack>

          {profileError ? <Alert severity="error">{profileError}</Alert> : null}

          {profileLoading ? (
            <Typography>Loading analytics...</Typography>
          ) : (
            <>
              <Grid container spacing={2} >
                <Grid item xs={12} md={2.9} sx={{ alignSelf: "flex-start" }}>
                  <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                    <Stack spacing={1}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Preferred Method
                      </Typography>
                      <Typography variant="h6">
                        {formatMethodLabel(learningAnalytics?.preferred_learning_method)}
                      </Typography>
                    </Stack>
                  </Box>
                </Grid>
                <Grid item xs={12} md={2.9} sx={{ alignSelf: "flex-start" }}>
                  <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                    <Stack spacing={1}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Average Quiz Score
                      </Typography>
                      <Typography variant="h6">
                        {learningAnalytics?.average_quiz_score ?? 0}%
                      </Typography>
                    </Stack>
                  </Box>
                </Grid>
                <Grid item xs={12} md={2.9} sx={{ alignSelf: "flex-start" }}>
                  <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                    <Stack spacing={1}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Lessons Completed
                      </Typography>
                      <Typography variant="h6">
                        {learningAnalytics?.total_lessons_completed ?? 0}
                      </Typography>
                    </Stack>
                  </Box>
                </Grid>
                <Grid item xs={12} md={2.9} sx={{ alignSelf: "flex-start" }}>
                  <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                    <Stack spacing={1}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Quiz Attempts
                      </Typography>
                      <Typography variant="h6">
                        {learningAnalytics?.total_quiz_attempts ?? 0}
                      </Typography>
                    </Stack>
                  </Box>
                </Grid>
              </Grid>

              <Stack direction="row" spacing={1} flexWrap="wrap">
                <Chip
                  label={`Average pass attempt: ${learningProfile?.average_attempts ?? 0}`}
                  size="small"
                />
                <Chip
                  label={`Adaptive results saved: ${learningAnalytics?.total_results ?? 0}`}
                  size="small"
                  variant="outlined"
                />
              </Stack>

              <Typography variant="h6">
                Performance by Learning Method
              </Typography>

              <Grid container spacing={2}>
                {Object.entries(methodLabelMap).map(([methodKey, label]) => {
                  const metrics = methodMetrics[methodKey] || {};

                  return (
                    <Grid key={methodKey} item xs={12} md={3.9} sx={{ alignSelf: "flex-start" }} >
                      <Box sx={{ p: 2, height: '100%', border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                        <Stack spacing={1.5}>
                          <Typography variant="h6">{label}</Typography>
                          <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" >
                            <Chip
                              label={`Success Rate: ${metrics.success_rate ?? 0}%`}
                              size="small"
                              color="primary"
                            />
                            <Chip
                              label={`Used: ${metrics.usage_count ?? 0}`}
                              size="small"
                              variant="outlined"
                            />
                          </Stack>
                          <Typography variant="body2" color="text.secondary">
                            Average score: {metrics.average_score ?? 0}%
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Total attempts: {metrics.total_attempts ?? 0}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Successful attempts: {metrics.successful_attempts ?? 0}
                          </Typography>
                        </Stack>
                      </Box>
                    </Grid>
                  );
                })}
              </Grid>
            </>
          )}
        </Stack>
      </Paper>

      <Paper sx={{ p: { xs: 3, md: 4 } }}>
        <Typography variant="h5" gutterBottom>
          Change Password
        </Typography>

        <Stack component="form" spacing={2} marginTop={3} onSubmit={handleSubmit} sx={{ maxWidth: 520 }}>
          {message ? <Alert severity="success">{message}</Alert> : null}
          {error ? <Alert severity="error">{error}</Alert> : null}

          <TextField
            label="Current Password"
            name="current_password"
            value={formData.current_password}
            onChange={handleChange}
            required
            type="password"
            fullWidth
          />
          <TextField
            label="New Password"
            name="new_password"
            value={formData.new_password}
            onChange={handleChange}
            required
            type="password"
            fullWidth
          />

          <Button type="submit" variant="contained" disabled={loading} sx={{ alignSelf: 'flex-start' }}>
            {loading ? 'Updating...' : 'Update Password'}
          </Button>
        </Stack>
      </Paper>
    </Stack>
  );
}
