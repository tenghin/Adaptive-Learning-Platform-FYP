import {
  Button,
  Card,
  CardActions,
  CardContent,
  Chip,
  LinearProgress,
  Stack,
  Typography,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { cardActionsSx, cardContentSx, interactiveCardSx, lineClampSx } from './cardStyles';

function getStatusDisplay(status) {
  if (status === 'completed') {
    return { label: 'Completed', color: 'success' };
  }

  if (status === 'in_progress') {
    return { label: 'In Progress', color: 'warning' };
  }

  return { label: 'Not Started', color: 'default' };
}

export function LessonCard({ lesson, progress }) {
  const status = progress?.status || 'not_started';
  const statusDisplay = getStatusDisplay(status);
  const progressValue = progress?.completion_percentage ?? 0;

  return (
    <Card
      sx={{
        ...interactiveCardSx,
        minHeight: 264,
      }}
    >
      <CardContent sx={cardContentSx}>
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          <Chip
            label={`Lesson ${lesson.order_index}`}
            size="small"
            variant="outlined"
          />
          <Chip
            label={`${lesson.estimated_minutes} mins`}
            size="small"
            variant="outlined"
          />
          <Chip
            label={statusDisplay.label}
            size="small"
            color={statusDisplay.color}
            variant={status === 'not_started' ? 'outlined' : 'filled'}
          />
        </Stack>

        <Typography variant="h6" sx={lineClampSx(2)}>
          {lesson.title}
        </Typography>

        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            ...lineClampSx(3),
            minHeight: '4.125rem',
          }}
        >
          {lesson.description || 'Open the lesson to begin learning.'}
        </Typography>

        {progress ? (
          <Stack spacing={1}>
            <LinearProgress
              variant="determinate"
              value={progressValue}
              sx={{ height: 8, borderRadius: 999 }}
            />
            <Typography variant="caption" color="text.secondary">
              {progressValue}% complete
            </Typography>
          </Stack>
        ) : null}
      </CardContent>

      <CardActions sx={cardActionsSx}>
        <Button
          component={RouterLink}
          to={`/lessons/${lesson.id}`}
          variant="contained"
          size="small"
        >
          Open Lesson
        </Button>
      </CardActions>
    </Card>
  );
}
