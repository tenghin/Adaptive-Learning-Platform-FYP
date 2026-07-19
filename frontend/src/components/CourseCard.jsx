import {
  Button,
  Card,
  CardActions,
  CardContent,
  Chip,
  Stack,
  Typography,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { cardActionsSx, cardContentSx, interactiveCardSx, lineClampSx } from './cardStyles';

export function CourseCard({ course, descriptionLines = 3 }) {
  return (
    <Card
      sx={{
        ...interactiveCardSx,
        minHeight: 280,
      }}
    >
      <CardContent sx={cardContentSx}>
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          <Chip
            label={course.difficulty_level}
            size="small"
            color="primary"
          />
          <Chip
            label={`${course.estimated_minutes} mins`}
            size="small"
            variant="outlined"
          />
        </Stack>

        <Typography variant="h6" sx={lineClampSx(2)}>
          {course.title}
        </Typography>

        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            ...lineClampSx(descriptionLines),
            minHeight: `${descriptionLines * 1.375}rem`,
          }}
        >
          {course.description}
        </Typography>
      </CardContent>

      <CardActions sx={cardActionsSx}>
        <Button
          component={RouterLink}
          to={`/courses/${course.id}`}
          variant="contained"
          size="small"
        >
          Open Course
        </Button>
      </CardActions>
    </Card>
  );
}
