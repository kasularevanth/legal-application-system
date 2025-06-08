// ============ src/store/slices/formsSlice.ts ============
import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { formsAPI } from "../../services/api/forms";

interface FormTemplate {
  id: number;
  name: string;
  form_type: string;
  description: string;
  language: string; // Added this property
  court_types: string[]; // Added this property
  template_json: any;
  fields: FormField[];
}

interface FormField {
  id: number;
  field_name: string;
  field_type: string;
  label: string;
  description: string;
  is_required: boolean;
  validation_rules: any;
  options: string[];
  order: number;
}

interface Application {
  id: number;
  application_id: string;
  title: string;
  status: string;
  form_data: any;
  template: {
    name: string;
    form_type: string;
  };
  created_at: string;
  updated_at: string;
  submitted_at?: string;
  generated_document_url?: string;
}

interface FormsState {
  templates: FormTemplate[];
  applications: Application[];
  currentApplication: Application | null;
  loading: boolean;
  error: string | null;
}

const initialState: FormsState = {
  templates: [],
  applications: [],
  currentApplication: null,
  loading: false,
  error: null,
};

export const fetchFormTemplates = createAsyncThunk(
  "forms/fetchTemplates",
  async (_, { rejectWithValue }) => {
    try {
      const response = await formsAPI.getTemplates();
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to fetch templates"
      );
    }
  }
);

export const fetchUserApplications = createAsyncThunk(
  "forms/fetchUserApplications",
  async (_, { rejectWithValue }) => {
    try {
      const response = await formsAPI.getUserApplications();
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to fetch applications"
      );
    }
  }
);

export const createApplication = createAsyncThunk(
  "forms/createApplication",
  async (
    applicationData: {
      template_id: number;
      title: string;
      form_data: any;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await formsAPI.createApplication(applicationData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to create application"
      );
    }
  }
);

export const updateApplication = createAsyncThunk(
  "forms/updateApplication",
  async ({ id, data }: { id: number; data: any }, { rejectWithValue }) => {
    try {
      const response = await formsAPI.updateApplication(id, data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to update application"
      );
    }
  }
);

export const submitApplication = createAsyncThunk(
  "forms/submitApplication",
  async (id: number, { rejectWithValue }) => {
    try {
      const response = await formsAPI.submitApplication(id);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to submit application"
      );
    }
  }
);

export const fetchApplicationDetails = createAsyncThunk(
  "forms/fetchApplicationDetails",
  async (id: number, { rejectWithValue }) => {
    try {
      const response = await formsAPI.getApplication(id);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to fetch application details"
      );
    }
  }
);

const formsSlice = createSlice({
  name: "forms",
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setCurrentApplication: (
      state,
      action: PayloadAction<Application | null>
    ) => {
      state.currentApplication = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Templates
      .addCase(fetchFormTemplates.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchFormTemplates.fulfilled, (state, action) => {
        state.loading = false;
        state.templates = action.payload;
      })
      .addCase(fetchFormTemplates.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Fetch User Applications
      .addCase(fetchUserApplications.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserApplications.fulfilled, (state, action) => {
        state.loading = false;
        state.applications = action.payload;
      })
      .addCase(fetchUserApplications.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Fetch Application Details
      .addCase(fetchApplicationDetails.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.currentApplication = null;
      })
      .addCase(
        fetchApplicationDetails.fulfilled,
        (state, action: PayloadAction<Application>) => {
          state.loading = false;
          state.currentApplication = action.payload;
        }
      )
      .addCase(fetchApplicationDetails.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
        state.currentApplication = null;
      })
      // Create Application
      .addCase(createApplication.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createApplication.fulfilled, (state, action) => {
        state.loading = false;
        state.applications.unshift(action.payload);
        state.currentApplication = action.payload;
      })
      .addCase(createApplication.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Update Application
      .addCase(updateApplication.fulfilled, (state, action) => {
        const index = state.applications.findIndex(
          (app) => app.id === action.payload.id
        );
        if (index !== -1) {
          state.applications[index] = action.payload;
        }
        state.currentApplication = action.payload;
      })
      // Submit Application
      .addCase(submitApplication.fulfilled, (state, action) => {
        const index = state.applications.findIndex(
          (app) => app.id === action.payload.id
        );
        if (index !== -1) {
          state.applications[index] = action.payload;
        }
        state.currentApplication = action.payload;
      });
  },
});

export const { clearError, setCurrentApplication } = formsSlice.actions;
export default formsSlice.reducer;
