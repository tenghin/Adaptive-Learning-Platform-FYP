import { Box, Button, Paper, Stack, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

export function NotFoundPage() {
  return (
    <Box sx={{ minHeight: '100vh', display: 'grid', placeItems: 'center', px: 2 }}>
      <Paper sx={{ p: 4, textAlign: 'center', maxWidth: 520 }}>
        <Stack spacing={2}>
          <Typography variant="h3">404</Typography>
          <Typography variant="h6">Page not found</Typography>
          <Button component={RouterLink} to="/dashboard" variant="contained">
            Go to dashboard
          </Button>
        </Stack>
      </Paper>
    </Box>
  );
}
