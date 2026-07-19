import { useEffect, useState } from 'react';
import { Box, Grid, Paper, Typography } from '@mui/material';
import { courseService } from '../services/courseService';
import { CourseCard } from '../components/CourseCard';
import { getErrorMessage } from '../utils/apiResponse';

export function CourseListPage() {
  const [courses, setCourses] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadCourses = async () => {
      try {
        const data = await courseService.listCourses();
        setCourses(data.courses || []);
      } catch (courseError) {
        setError(getErrorMessage(courseError));
      }
    };

    loadCourses();
  }, []);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Courses
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Browse the available learning paths.
      </Typography>

      {error ? (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography color="error">{error}</Typography>
        </Paper>
      ) : null}

      <Grid container spacing={3}>
        {courses.map((course) => (
          <Grid key={course.id} item xs={12} sm={6} lg={4}>
            <CourseCard course={course} />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
