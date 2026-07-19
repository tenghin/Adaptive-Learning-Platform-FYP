import { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Button,
  Card,
  CardContent,
  Switch,
  Divider,
  FormControl,
  FormControlLabel,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  TextField,
  Typography,
  Chip,
} from '@mui/material';
import { courseService } from '../services/courseService';
import { lessonService } from '../services/lessonService';
import { getErrorMessage } from '../utils/apiResponse';

import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';

const courseTemplate = {
  title: '',
  description: '',
  difficulty_level: 'beginner',
  estimated_minutes: 60,
  is_published: true,
};

const lessonTemplate = {
  title: '',
  content: '',
  summary: '',
  order_index: 1,
  estimated_minutes: 15,
  is_published: true,
};

function toBooleanValue(value) {
  return Boolean(value);
}

export function AdminManagementPage() {
  const [courses, setCourses] = useState([]);
  const [selectedCourseId, setSelectedCourseId] = useState('');
  const [lessons, setLessons] = useState([]);
  const [courseForm, setCourseForm] = useState(courseTemplate);
  const [lessonForm, setLessonForm] = useState(lessonTemplate);
  const [editingCourseId, setEditingCourseId] = useState(null);
  const [editingLessonId, setEditingLessonId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [courseSaving, setCourseSaving] = useState(false);
  const [lessonSaving, setLessonSaving] = useState(false);
  const [showCourseForm, setShowCourseForm] = useState(false);
  const [showLessonForm, setShowLessonForm] = useState(false);

  const selectedCourse = useMemo(
    () => courses.find((course) => String(course.id) === String(selectedCourseId)),
    [courses, selectedCourseId]
  );

  const loadCourses = async (preferredSelectedCourseId = '') => {
    const data = await courseService.listCourses();
    const sortedCourses = data.courses || [];
    setCourses(sortedCourses);

    if (preferredSelectedCourseId) {
      const matchingCourse = sortedCourses.find(
        (course) => String(course.id) === String(preferredSelectedCourseId)
      );

      if (matchingCourse) {
        setSelectedCourseId(String(matchingCourse.id));
        return;
      }
    }

    if (!selectedCourseId && sortedCourses.length) {
      setSelectedCourseId(String(sortedCourses[0].id));
    }
  };

  const loadLessons = async (courseId) => {
    if (!courseId) {
      setLessons([]);
      return;
    }

    const data = await courseService.listLessons(courseId);
    setLessons(data.lessons || []);
  };

  const refreshAll = async (nextSelectedCourseId = selectedCourseId) => {
    await loadCourses(nextSelectedCourseId);
    await loadLessons(nextSelectedCourseId);
  };

  useEffect(() => {
    const initialize = async () => {
      try {
        await loadCourses();
      } catch (adminError) {
        setError(getErrorMessage(adminError));
      } finally {
        setLoading(false);
      }
    };

    initialize();
  }, []);

  useEffect(() => {
    const initializeLessons = async () => {
      if (!selectedCourseId) {
        setLessons([]);
        return;
      }

      try {
        await loadLessons(selectedCourseId);
      } catch (adminError) {
        setError(getErrorMessage(adminError));
      }
    };

    initializeLessons();
  }, [selectedCourseId]);

  const resetCourseForm = () => {
    setCourseForm(courseTemplate);
    setEditingCourseId(null);
    setShowCourseForm(false);
  };

  const resetLessonForm = () => {
    setLessonForm(lessonTemplate);
    setEditingLessonId(null);
    setShowLessonForm(false);
  };

  const handleCourseSubmit = async (event) => {
    event.preventDefault();
    setCourseSaving(true);
    setError('');

    try {
      let savedCourseId = editingCourseId;

      if (editingCourseId) {
        await courseService.updateCourse(editingCourseId, courseForm);
      } else {
        const responseData = await courseService.createCourse(courseForm);
        savedCourseId = responseData.course?.id || null;
      }

      await refreshAll(savedCourseId || selectedCourseId);
      if (savedCourseId) {
        setSelectedCourseId(String(savedCourseId));
      }
      resetCourseForm();
    } catch (adminError) {
      setError(getErrorMessage(adminError));
    } finally {
      setCourseSaving(false);
    }
  };

  const handleLessonSubmit = async (event) => {
    event.preventDefault();
    if (!selectedCourseId) {
      return;
    }

    setLessonSaving(true);
    setError('');

    try {
      if (editingLessonId) {
        await lessonService.updateLesson(editingLessonId, lessonForm);
      } else {
        await lessonService.createLesson(selectedCourseId, lessonForm);
      }

      await loadLessons(selectedCourseId);
      resetLessonForm();
    } catch (adminError) {
      setError(getErrorMessage(adminError));
    } finally {
      setLessonSaving(false);
    }
  };

  const handleEditCourse = (course) => {
    setShowCourseForm(true);
    
    setEditingCourseId(course.id);
    setCourseForm({
      title: course.title,
      description: course.description,
      difficulty_level: course.difficulty_level,
      estimated_minutes: course.estimated_minutes,
      is_published: course.is_published,
    });
  };

  const handleEditLesson = (lesson) => {
    setShowLessonForm(true);

    setEditingLessonId(lesson.id);
    setLessonForm({
      title: lesson.title,
      content: lesson.content || '',
      summary: lesson.summary || '',
      order_index: lesson.order_index,
      estimated_minutes: lesson.estimated_minutes,
      is_published: lesson.is_published,
    });
  };

  const handleDeleteCourse = async (courseId) => {
    if (!window.confirm('Delete this course and its lessons?')) {
      return;
    }

    try {
      await courseService.deleteCourse(courseId);
      const nextSelected = String(courseId) === String(selectedCourseId) ? '' : selectedCourseId;
      if (String(courseId) === String(selectedCourseId)) {
        resetLessonForm();
      }
      await refreshAll(nextSelected);
    } catch (adminError) {
      setError(getErrorMessage(adminError));
    }
  };

  const handleDeleteLesson = async (lessonId) => {
    if (!window.confirm('Delete this lesson?')) {
      return;
    }

    try {
      await lessonService.deleteLesson(lessonId);
      await loadLessons(selectedCourseId);
      if (String(lessonId) === String(editingLessonId)) {
        resetLessonForm();
      }
    } catch (adminError) {
      setError(getErrorMessage(adminError));
    }
  };

  const handleSelectCourse = (courseId) => {
    setSelectedCourseId(String(courseId));
  };

  const handleCourseCardKeyDown = (event, courseId) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleSelectCourse(courseId);
    }
  };

  const stopCourseCardClick = (event) => {
    event.stopPropagation();
  };

  if (loading) {
    return <Typography>Loading admin tools...</Typography>;
  }

  return (
    <Stack spacing={3}>
      <Paper sx={{ p: { xs: 3, md: 4 } }}>
        <Stack spacing={1}>
          <Typography variant="overline" color="text.secondary">
            Administrator
          </Typography>
          <Typography variant="h4">Course and Lesson Management</Typography>
          <Typography variant="body1" color="text.secondary">
            Create, update, publish, and delete courses and lessons for the prototype.
          </Typography>
        </Stack>
      </Paper>

      {error ? <Alert severity="error">{error}</Alert> : null}

      <Paper sx={{ p: { xs: 3, md: 4 } }}>
        <Stack spacing={3}>
          <Stack spacing={1}>
            <Typography variant="h5">Courses</Typography>
            <Typography variant="body2" color="text.secondary">
              Manage course metadata and publication state.
            </Typography>
          </Stack>

          <Stack spacing={2}>
            {courses.map((course) => (
              <Card
                key={course.id}
                variant={String(course.id) === String(selectedCourseId) ? 'elevation' : 'outlined'}
                role="button"
                tabIndex={0}
                onClick={() => handleSelectCourse(course.id)}
                onKeyDown={(event) => handleCourseCardKeyDown(event, course.id)}
                sx={{
                  cursor: 'pointer',
                  borderWidth: String(course.id) === String(selectedCourseId) ? 2 : 1,
                  borderColor: String(course.id) === String(selectedCourseId) ? 'primary.main' : 'divider',
                  boxShadow: String(course.id) === String(selectedCourseId) ? 6 : 0,
                  transition: 'transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: 4,
                  },
                  '&:active': {
                    transform: 'scale(0.985)',
                  },
                  '&:focus-visible': {
                    outline: '2px solid',
                    outlineColor: 'primary.main',
                    outlineOffset: 2,
                  },
                }}
              >
                <CardContent>
                  <Stack spacing={2}>
                    <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
                      <Typography variant="h6">{course.title}</Typography>
                      <Stack direction="row" spacing={1} flexWrap="wrap">
                        <Chip
                          label={course.difficulty_level}
                          size="small"
                        />

                        <Chip
                          label={`${course.estimated_minutes} mins`}
                          size="small"
                        />

                        <Chip
                          label={course.is_published ? "Published" : "Draft"}
                          color={course.is_published ? "success" : "warning"}
                          size="small"
                        />
                        {String(course.id) === String(selectedCourseId) ? (
                          <Chip
                            label="Selected"
                            color="primary"
                            size="small"
                            variant="filled"
                          />
                        ) : null}
                      </Stack>
                    </Stack>
                    <Typography variant="body2" color="text.secondary">
                      {course.description}
                    </Typography>
                    <Stack direction="row" spacing={1} flexWrap="wrap">
                      <Button
                        variant="text"
                        startIcon={<EditIcon />}
                        onClick={(event) => {
                          stopCourseCardClick(event);
                          handleEditCourse(course);
                        }}
                      >
                        Edit
                      </Button>
                      <Button
                        color="error"
                        startIcon={<DeleteIcon />}
                        onClick={(event) => {
                          stopCourseCardClick(event);
                          handleDeleteCourse(course.id);
                        }}
                      >
                        Delete
                      </Button>
                    </Stack>
                  </Stack>
                </CardContent>
              </Card>
            ))}
          </Stack>

          <Divider />

          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setShowCourseForm(!showCourseForm)}
            sx={{ alignSelf: "flex-start" }}
          >
            {showCourseForm
              ? editingCourseId
                ? "Hide Edit Course"
                : "Hide Create Course"
              : editingCourseId
                ? "Edit Course"
                : "Create Course"}
          </Button>

          
          {showCourseForm && (
            <Stack component="form" spacing={2} onSubmit={handleCourseSubmit} sx={{ maxWidth: 760 }}> 
                    <Typography variant="h6">
                      {editingCourseId ? 'Edit Course' : 'Create Course'}
                    </Typography>

                    <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
                      <TextField
                        label="Title"
                        value={courseForm.title}
                        onChange={(event) => setCourseForm((current) => ({ ...current, title: event.target.value }))}
                        fullWidth
                        required
                      />
                      <FormControl fullWidth>
                        <InputLabel>Difficulty</InputLabel>
                        <Select
                          label="Difficulty"
                          value={courseForm.difficulty_level}
                          onChange={(event) => setCourseForm((current) => ({ ...current, difficulty_level: event.target.value }))}
                        >
                          <MenuItem value="beginner">Beginner</MenuItem>
                          <MenuItem value="intermediate">Intermediate</MenuItem>
                          <MenuItem value="advanced">Advanced</MenuItem>
                        </Select>
                      </FormControl>
                    </Stack>

                    <TextField
                      label="Description"
                      value={courseForm.description}
                      onChange={(event) => setCourseForm((current) => ({ ...current, description: event.target.value }))}
                      multiline
                      minRows={3}
                      fullWidth
                      required
                    />

                    <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems="center">
                      <TextField
                        label="Estimated Minutes"
                        type="number"
                        value={courseForm.estimated_minutes}
                        onChange={(event) => setCourseForm((current) => ({ ...current, estimated_minutes: Number(event.target.value) }))}
                        fullWidth
                      />
                      <FormControlLabel
                        control={
                          <Switch
                            checked={toBooleanValue(courseForm.is_published)}
                            onChange={(event) => setCourseForm((current) => ({ ...current, is_published: event.target.checked }))}
                          />
                        }
                        label="Published"
                      />
                    </Stack>

                    <Stack direction="row" spacing={1} flexWrap="wrap">
                      <Button type="submit" variant="contained" disabled={courseSaving}>
                        {courseSaving ? 'Saving...' : editingCourseId ? 'Update Course' : 'Create Course'}
                      </Button>
                      {editingCourseId ? (
                        <Button variant="text" onClick={resetCourseForm}>
                          Cancel edit
                        </Button>
                      ) : null}
                    </Stack>
            </Stack>
          )}
        </Stack> 
      </Paper>

      <Paper sx={{ p: { xs: 3, md: 4 } }}>
        <Stack spacing={3}>
          <Stack spacing={1}>
            <Typography variant="h5">Lessons</Typography>
            <Typography variant="body2" color="text.secondary">
              Manage lessons for the selected course.
            </Typography>
          </Stack>

          {!selectedCourse ? (
            <Alert severity="info">Select a course to manage its lessons.</Alert>
          ) : (
            <>
              <Typography variant="body2" color="text.secondary">
                Editing lessons for <strong>{selectedCourse.title}</strong>
              </Typography>

              <Stack spacing={2}>
                {[...lessons]
                  .sort((a, b) => a.order_index - b.order_index)
                  .map((lesson) => (
                  <Card key={lesson.id} variant="outlined">
                    <CardContent>
                      <Stack spacing={2}>
                        <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
                          <Typography variant="h6">{lesson.title}</Typography>
                          <Stack direction="row" spacing={1} flexWrap="wrap">
                            <Chip
                              label={`Lesson ${lesson.order_index}`}
                              size="small"
                            />

                            <Chip
                              label={`${lesson.estimated_minutes} mins`}
                              size="small"
                            />

                            <Chip
                              label={lesson.is_published ? "Published" : "Draft"}
                              color={lesson.is_published ? "success" : "warning"}
                              size="small"
                            />
                          </Stack>
                        </Stack>
                        <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-wrap' }}>
                          {lesson.summary || lesson.content}
                        </Typography>
                        <Stack direction="row" spacing={1} flexWrap="wrap">
                          <Button
                              variant="outlined"
                              startIcon={<EditIcon />}
                              onClick={() => handleEditLesson(lesson)}
                          >
                            Edit
                          </Button>
                          <Button color="error" startIcon={<DeleteIcon />} onClick={() => handleDeleteLesson(lesson.id)}>
                            Delete
                          </Button>
                        </Stack>
                      </Stack>
                    </CardContent>
                  </Card>
                ))}
              </Stack>

              <Divider />

              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setShowLessonForm(!showLessonForm)}
                sx={{ alignSelf: "flex-start" }}
              >
                {showLessonForm
                  ? editingLessonId
                    ? "Hide Edit Lesson"
                    : "Hide Create Lesson"
                  : editingLessonId
                    ? "Edit Lesson"
                    : "Create Lesson"}
              </Button>
        
              {showLessonForm && (
                <Stack component="form" spacing={2} onSubmit={handleLessonSubmit} sx={{ maxWidth: 900 }}>
                  <Typography variant="h6">
                    {editingLessonId ? 'Edit Lesson' : 'Create Lesson'}
                  </Typography>

                  <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
                    <TextField
                      label="Title"
                      value={lessonForm.title}
                      onChange={(event) => setLessonForm((current) => ({ ...current, title: event.target.value }))}
                      fullWidth
                      required
                    />
                    <TextField
                      label="Order Index"
                      type="number"
                      value={lessonForm.order_index}
                      onChange={(event) => setLessonForm((current) => ({ ...current, order_index: Number(event.target.value) }))}
                      fullWidth
                    />
                  </Stack>

                  <TextField
                    label="Content"
                    value={lessonForm.content}
                    onChange={(event) => setLessonForm((current) => ({ ...current, content: event.target.value }))}
                    multiline
                    minRows={5}
                    fullWidth
                    required
                  />

                  <TextField
                    label="Summary"
                    value={lessonForm.summary}
                    onChange={(event) => setLessonForm((current) => ({ ...current, summary: event.target.value }))}
                    multiline
                    minRows={3}
                    fullWidth
                  />

                  <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems="center">
                    <TextField
                      label="Estimated Minutes"
                      type="number"
                      value={lessonForm.estimated_minutes}
                      onChange={(event) => setLessonForm((current) => ({ ...current, estimated_minutes: Number(event.target.value) }))}
                      fullWidth
                    />
                    <FormControlLabel
                      control={
                        <Switch
                          checked={toBooleanValue(lessonForm.is_published)}
                          onChange={(event) => setLessonForm((current) => ({ ...current, is_published: event.target.checked }))}
                        />
                      }
                      label="Published"
                    />
                  </Stack>

                  <Stack direction="row" spacing={1} flexWrap="wrap">
                    <Button startIcon={<AddIcon />} type="submit" variant="contained" disabled={lessonSaving}>
                      {lessonSaving ? 'Saving...' : editingLessonId ? 'Update Lesson' : 'Create Lesson'}
                    </Button>
                    {editingLessonId ? (
                      <Button variant="text" onClick={resetLessonForm}>
                        Cancel edit
                      </Button>
                    ) : null}
                  </Stack>
                </Stack>
              )}
            </>
          )}
        </Stack>
      </Paper>
    </Stack>
  );
}
