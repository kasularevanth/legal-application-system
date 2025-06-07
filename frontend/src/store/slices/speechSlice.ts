// ============ src/store/slices/speechSlice.ts ============
import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { speechAPI } from "../../services/api/speech";

interface SpeechState {
  isRecording: boolean;
  isProcessing: boolean;
  transcription: string;
  confidence: number;
  language: string;
  audioUrl?: string;
  recognition: any;
  error: string | null;
}

const initialState: SpeechState = {
  isRecording: false,
  isProcessing: false,
  transcription: "",
  confidence: 0,
  language: "hi",
  recognition: null,
  error: null,
};

export const speechToText = createAsyncThunk(
  "speech/speechToText",
  async (audioData: { file: File; language: string }, { rejectWithValue }) => {
    try {
      const formData = new FormData();
      formData.append("audio", audioData.file);
      formData.append("language", audioData.language);

      const response = await speechAPI.speechToText(formData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || "Speech recognition failed"
      );
    }
  }
);

export const textToSpeech = createAsyncThunk(
  "speech/textToSpeech",
  async (textData: { text: string; language: string }, { rejectWithValue }) => {
    try {
      const response = await speechAPI.textToSpeech(textData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || "Text to speech failed"
      );
    }
  }
);

export const analyzeSpeechForForm = createAsyncThunk(
  "speech/analyzeSpeechForForm",
  async (
    data: { transcribed_text: string; template_id: number },
    { rejectWithValue }
  ) => {
    try {
      const response = await speechAPI.analyzeSpeech(data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || "Speech analysis failed"
      );
    }
  }
);

const speechSlice = createSlice({
  name: "speech",
  initialState,
  reducers: {
    startRecording: (state) => {
      state.isRecording = true;
      state.error = null;
    },
    stopRecording: (state) => {
      state.isRecording = false;
    },
    setTranscription: (state, action: PayloadAction<string>) => {
      state.transcription = action.payload;
    },
    setLanguage: (state, action: PayloadAction<string>) => {
      state.language = action.payload;
    },
    setSpeechRecognition: (state, action: PayloadAction<any>) => {
      state.recognition = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    resetSpeech: (state) => {
      state.transcription = "";
      state.confidence = 0;
      state.audioUrl = undefined;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(speechToText.pending, (state) => {
        state.isProcessing = true;
        state.error = null;
      })
      .addCase(speechToText.fulfilled, (state, action) => {
        state.isProcessing = false;
        state.transcription = action.payload.transcription;
        state.confidence = action.payload.confidence;
      })
      .addCase(speechToText.rejected, (state, action) => {
        state.isProcessing = false;
        state.error = action.payload as string;
      })
      .addCase(textToSpeech.pending, (state) => {
        state.isProcessing = true;
        state.error = null;
      })
      .addCase(textToSpeech.fulfilled, (state, action) => {
        state.isProcessing = false;
        state.audioUrl = action.payload.audio_url;
      })
      .addCase(textToSpeech.rejected, (state, action) => {
        state.isProcessing = false;
        state.error = action.payload as string;
      });
  },
});

export const {
  startRecording,
  stopRecording,
  setTranscription,
  setLanguage,
  setSpeechRecognition,
  clearError,
  resetSpeech,
} = speechSlice.actions;

export default speechSlice.reducer;
