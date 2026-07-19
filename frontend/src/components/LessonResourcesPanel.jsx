import {
  Button,
  Chip,
  Paper,
  Stack,
  Typography,
} from "@mui/material";

import DescriptionIcon from "@mui/icons-material/Description";
import ImageIcon from "@mui/icons-material/Image";
import SlideshowIcon from "@mui/icons-material/Slideshow";
import { lessonService } from "../services/lessonService";
import { learningActivityService } from "../services/learningActivityService";

function getMaterialIcon(mimeType) {

    if (!mimeType) return <DescriptionIcon />;

    if (mimeType.startsWith("image/")) {
        return <ImageIcon />;
    }

    if (mimeType.includes("presentation")) {
        return <SlideshowIcon />;
    }

    return <DescriptionIcon />;
}

export function LessonResourcesPanel({
    resources,
    isAdmin,
    onDeleted,
}) {
  if (!resources?.length) {
    return (
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Typography variant="body1" color="text.secondary">
          No lesson resources have been uploaded or generated yet.
        </Typography>
      </Paper>
    );
  }

  const visibleResources = resources.filter((resource) => {
    return resource.resource_type === "material";
  });

  const handleDeleteMaterial = async (resourceId) => {

    if (!window.confirm("Delete this learning material?")) {
        return;
    }

    try {

        await lessonService.deleteLearningMaterial(
            resourceId
        );

        onDeleted?.();

    } catch (error) {

        console.error(error);

    }

  };

  if (!visibleResources.length) {
    return null;
  }
  
  const handleOpenMaterial = async (resource) => {
    try {
        const blob = await lessonService.downloadLearningMaterial(resource.id);

        const url = URL.createObjectURL(blob);

        window.open(url, "_blank");

        URL.revokeObjectURL(url);

        await learningActivityService.recordActivity({
            lesson_id: resource.lesson_id,
            activity_type: "material_opened",
        });
        
    } catch (error) {
        console.error(error);
    }
};

  return (
    <Stack spacing={2}>
      {visibleResources.map((resource) => (
        <Paper
          key={resource.id}
          variant="outlined"
          sx={{
            p: 2.5,
            borderColor: 'rgba(18, 50, 79, 0.12)',
            background: "#ffffff",
          }}
        >
          <Stack spacing={1.25}>
            <Stack direction="row" spacing={1} flexWrap="wrap" alignItems="center">
              
              <Stack direction="row" spacing={1} alignItems="center">
                  {getMaterialIcon(resource.mime_type)}

                  <Typography variant="h6">
                      {resource.title}
                  </Typography>
              </Stack>

              <Stack spacing={0.5}>

                <Typography
                    variant="body2"
                    color="text.secondary"
                >
                    {resource.file_name}
                </Typography>

              </Stack>
              
              <Chip
                  label={
                      resource.mime_type?.split("/")[1]?.toUpperCase()
                      ?? "FILE"
                  }
                  size="small"
              />
              
              {resource.is_generated ? (
                <Chip label="Generated" size="small" color="secondary" />
              ) : null}
            </Stack>

            <Stack
                direction="row"
                spacing={1}
            >
                
                <Button
                    variant="contained"
                    onClick={() => handleOpenMaterial(resource)}
                >
                    Open Material
                </Button>

                {isAdmin && (
                    <Button
                        variant="outlined"
                        color="error"
                        onClick={() =>
                            handleDeleteMaterial(resource.id)
                        }
                    >
                        Delete
                    </Button>
                )}

            </Stack>

            <Typography variant="caption" color="text.secondary">
              Updated {new Date(resource.updated_at).toLocaleString()}
            </Typography>
          </Stack>
        </Paper>
      ))}
    </Stack>
  );
}
