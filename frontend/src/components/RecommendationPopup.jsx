import { useState } from "react";
import {
    Box,
    Paper,
    Typography,
    Button,
    IconButton,
    Chip,
    Stack
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";

export function RecommendationPopup({
    recommendation,
    analytics,
    onContinue,
    isAdmin
}) {

    const [open, setOpen] = useState(true);

    if (!open) {
        return (
            <Button
                variant="contained"
                onClick={() => setOpen(true)}
                sx={{
                    position: "fixed",
                    bottom: 20,
                    right: 20,
                    zIndex: 2000
                }}
            >
                🎯
            </Button>
        );
    }

    return (
        <Box
            sx={{
                position: "fixed",
                bottom: 20,
                right: 20,
                width: 340,
                zIndex: 2000
            }}
        >
            <Paper elevation={8} sx={{ p: 2 }}>

                <Stack
                    direction="row"
                    justifyContent="space-between"
                    alignItems="center"
                >
                    <Typography variant="h6">
                        Recommended Next Step
                    </Typography>

                    <IconButton
                        size="small"
                        onClick={() => setOpen(false)}
                    >
                        <CloseIcon />
                    </IconButton>

                </Stack>

                <Typography
                    variant="subtitle1"
                    sx={{ mt: 2 }}
                >
                    {recommendation?.title}
                </Typography>

                <Typography
                    color="text.secondary"
                    sx={{ mb: 2 }}
                >
                    {recommendation?.reason}
                </Typography>

                <Button
                    fullWidth
                    variant="contained"
                    onClick={onContinue}
                >
                    Continue
                </Button>

                {/* {isAdmin && analytics && (
                    <Stack
                        spacing={1}
                        sx={{ mt: 2 }}
                    >
                        <Chip
                            label={`Average: ${analytics.average_score ?? "-"}`}
                        />

                        <Chip
                            label={`Trend: ${analytics.score_trend}`}
                        />

                        <Chip
                            label={`Consistency: ${analytics.score_consistency}`}
                        />
                    </Stack>
                )} */}

            </Paper>
        </Box>
    );
}