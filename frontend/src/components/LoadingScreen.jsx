import { Box, CircularProgress, Typography } from '@mui/material';

export function LoadingScreen() {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'grid',
        placeItems: 'center',
        gap: 2,
        background:
          'radial-gradient(circle at top, rgba(224, 159, 62, 0.16), transparent 36%), linear-gradient(180deg, #f7faff 0%, #edf3fb 100%)',
      }}
    >
      <CircularProgress />
      <Typography variant="subtitle1" color="text.secondary">
        Loading Adaptive Learning Platform
      </Typography>
    </Box>
  );
}
