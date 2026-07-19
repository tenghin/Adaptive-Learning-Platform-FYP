import { api } from "./api";
import { unwrapData } from "../utils/apiResponse";

async function recordActivity(payload) {
    const response = await api.post(
        "/api/learning-activities",
        payload
    );

    return unwrapData(response);
}

export const learningActivityService = {
    recordActivity,
};