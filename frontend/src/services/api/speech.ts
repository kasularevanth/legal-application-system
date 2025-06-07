// ============ src/services/api/speech.ts ============
import api from "./index";

export const speechAPI = {
  speechToText: (formData: FormData) =>
    api.post("/speech/speech-to-text/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }),

  textToSpeech: (data: { text: string; language: string }) =>
    api.post("/speech/text-to-speech/", data),

  analyzeSpeech: (data: { transcribed_text: string; template_id: number }) =>
    api.post("/speech/analyze-speech/", data),

  translateText: (data: {
    text: string;
    source_language: string;
    target_language: string;
  }) => api.post("/speech/translate/", data),
};
