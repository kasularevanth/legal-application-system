// src/store/slices/legalCaseSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { legalCaseAPI } from "../../services/api/legalCase";

interface CaseTypeMapping {
  [uuid: string]: string[];
}

interface QuestionMapping {
  [uuid: string]: string[];
}

interface LegalCaseState {
  // Case processing
  caseType: string | null;
  caseTypeConfidence: number;
  detectedKeywords: string[];

  // Questions and answers
  questions: string[];
  currentQuestionIndex: number;
  answers: Record<string, string>;
  questionMappings: QuestionMapping;

  // Document generation
  documentUrl: string | null;
  documentPreview: string | null;
  templateUsed: string | null;

  // Status tracking
  status:
    | "idle"
    | "processing"
    | "questioning"
    | "generating"
    | "completed"
    | "error";
  loading: boolean;
  error: string | null;

  // Processing metadata
  processingSteps: string[];
  currentStep: string | null;
}

const initialState: LegalCaseState = {
  caseType: null,
  caseTypeConfidence: 0,
  detectedKeywords: [],
  questions: [],
  currentQuestionIndex: 0,
  answers: {},
  questionMappings: {},
  documentUrl: null,
  documentPreview: null,
  templateUsed: null,
  status: "idle",
  loading: false,
  error: null,
  processingSteps: [],
  currentStep: null,
};

// Async thunks
export const processInitialInput = createAsyncThunk(
  "legalCase/processInitialInput",
  async (
    data: { text: string; mode: "voice" | "text"; language?: string },
    { rejectWithValue }
  ) => {
    try {
      const response = await legalCaseAPI.processInitialInput(data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to process input"
      );
    }
  }
);

export const submitAnswer = createAsyncThunk(
  "legalCase/submitAnswer",
  async (
    data: {
      questionIndex: number;
      answer: string;
      mode: "voice" | "text";
      caseType: string;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await legalCaseAPI.submitAnswer(data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to submit answer"
      );
    }
  }
);

export const generateDocument = createAsyncThunk(
  "legalCase/generateDocument",
  async (
    data: {
      caseType: string;
      answers: Record<string, string>;
      userId: number;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await legalCaseAPI.generateDocument(data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to generate document"
      );
    }
  }
);

export const getCaseTypeMappings = createAsyncThunk(
  "legalCase/getCaseTypeMappings",
  async (_, { rejectWithValue }) => {
    try {
      const response = await legalCaseAPI.getCaseTypeMappings();
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to fetch case type mappings"
      );
    }
  }
);

export const getQuestionMappings = createAsyncThunk(
  "legalCase/getQuestionMappings",
  async (caseType: string, { rejectWithValue }) => {
    try {
      const response = await legalCaseAPI.getQuestionMappings(caseType);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to fetch question mappings"
      );
    }
  }
);

const legalCaseSlice = createSlice({
  name: "legalCase",
  initialState,
  reducers: {
    resetCase: (state) => {
      return { ...initialState };
    },

    setCurrentStep: (state, action: PayloadAction<string>) => {
      state.currentStep = action.payload;
      if (!state.processingSteps.includes(action.payload)) {
        state.processingSteps.push(action.payload);
      }
    },

    nextQuestion: (state) => {
      if (state.currentQuestionIndex < state.questions.length - 1) {
        state.currentQuestionIndex += 1;
      }
    },

    previousQuestion: (state) => {
      if (state.currentQuestionIndex > 0) {
        state.currentQuestionIndex -= 1;
      }
    },

    updateAnswer: (
      state,
      action: PayloadAction<{ question: string; answer: string }>
    ) => {
      state.answers[action.payload.question] = action.payload.answer;
    },

    setQuestions: (state, action: PayloadAction<string[]>) => {
      state.questions = action.payload;
      state.currentQuestionIndex = 0;
      state.status = "questioning";
    },

    clearError: (state) => {
      state.error = null;
    },

    updateStatus: (state, action: PayloadAction<LegalCaseState["status"]>) => {
      state.status = action.payload;
    },
  },

  extraReducers: (builder) => {
    builder
      // Process Initial Input
      .addCase(processInitialInput.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.status = "processing";
        state.currentStep = "Analyzing input";
      })
      .addCase(processInitialInput.fulfilled, (state, action) => {
        state.loading = false;
        state.caseType = action.payload.caseType;
        state.caseTypeConfidence = action.payload.confidence;
        state.detectedKeywords = action.payload.keywords;
        state.questions = action.payload.questions;
        state.templateUsed = action.payload.templateId;
        state.status =
          action.payload.questions.length > 0 ? "questioning" : "generating";
        state.currentStep = "Case type determined";
      })
      .addCase(processInitialInput.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
        state.status = "error";
        state.currentStep = "Processing failed";
      })

      // Submit Answer
      .addCase(submitAnswer.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.currentStep = "Processing answer";
      })
      .addCase(submitAnswer.fulfilled, (state, action) => {
        state.loading = false;
        const { questionIndex, answer, nextQuestion } = action.payload;

        // Store the answer
        if (state.questions[questionIndex]) {
          state.answers[state.questions[questionIndex]] = answer;
        }

        // Move to next question or complete questioning
        if (nextQuestion) {
          state.currentQuestionIndex += 1;
        } else {
          state.status = "generating";
          state.currentStep = "All questions answered";
        }
      })
      .addCase(submitAnswer.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
        state.currentStep = "Answer processing failed";
      })

      // Generate Document
      .addCase(generateDocument.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.status = "generating";
        state.currentStep = "Generating document";
      })
      .addCase(generateDocument.fulfilled, (state, action) => {
        state.loading = false;
        state.documentUrl = action.payload.documentUrl;
        state.documentPreview = action.payload.preview;
        state.status = "completed";
        state.currentStep = "Document generated successfully";
      })
      .addCase(generateDocument.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
        state.status = "error";
        state.currentStep = "Document generation failed";
      })

      // Get Case Type Mappings
      .addCase(getCaseTypeMappings.fulfilled, (state, action) => {
        // Store mappings in state if needed
      })

      // Get Question Mappings
      .addCase(getQuestionMappings.fulfilled, (state, action) => {
        state.questionMappings = action.payload;
      });
  },
});

export const {
  resetCase,
  setCurrentStep,
  nextQuestion,
  previousQuestion,
  updateAnswer,
  setQuestions,
  clearError,
  updateStatus,
} = legalCaseSlice.actions;

export default legalCaseSlice.reducer;
