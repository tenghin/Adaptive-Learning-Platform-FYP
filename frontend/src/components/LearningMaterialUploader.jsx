import { useState } from "react";
import {
    Button,
    Stack,
    TextField,
} from "@mui/material";

import { lessonService } from "../services/lessonService";

export function LearningMaterialUploader({
    lessonId,
    onUploaded,
}) {

    const [title, setTitle] = useState("");
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);

    const handleUpload = async () => {

        console.log("========== UPLOAD ==========");
        console.log("lessonId:", lessonId);
        console.log("title:", title);
        console.log("file:", file);

        if (!file) {
            console.log("No file selected.");
            return;
        }

        setUploading(true);

        try {

            const formData = new FormData();

            formData.append("title", title);
            formData.append("file", file);

            console.log("Sending upload request...");

            const response =
                await lessonService.uploadLearningMaterial(
                    lessonId,
                    formData
                );

            console.log("Upload succeeded!");
            console.log(response);

            setTitle("");
            setFile(null);

            onUploaded?.();

        } catch (error) {

            console.error("Upload failed:");
            console.error(error.response?.data);
            console.error(error);

        } finally {

            setUploading(false);

        }
    };

    return (
        <Stack spacing={2}>

            <TextField
                label="Material Title"
                value={title}
                onChange={(event) =>
                    setTitle(event.target.value)
                }
            />

            <Button
                component="label"
                variant="outlined"
            >
                Choose File

                <input
                    hidden
                    type="file"
                    onChange={(event) =>
                        setFile(event.target.files?.[0] ?? null)
                    }
                />
            </Button>

            <Button
                variant="contained"
                disabled={!file || uploading}
                onClick={handleUpload}
            >
                {uploading
                    ? "Uploading..."
                    : "Upload Learning Material"}
            </Button>

        </Stack>
    );
}