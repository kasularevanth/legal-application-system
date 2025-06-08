// src/services/api/legalCase.ts
import api from "./index";

export interface ProcessInitialInputRequest {
  text: string;
  mode: "voice" | "text";
  language?: string;
}

export interface ProcessInitialInputResponse {
  caseType: string;
  confidence: number;
  keywords: string[];
  questions: string[];
  templateId: string;
  requiresQuestions: boolean;
}

export interface SubmitAnswerRequest {
  questionIndex: number;
  answer: string;
  mode: "voice" | "text";
  caseType: string;
}

export interface SubmitAnswerResponse {
  questionIndex: number;
  answer: string;
  nextQuestion: boolean;
  validationErrors?: string[];
}

export interface GenerateDocumentRequest {
  caseType: string;
  answers: Record<string, string>;
  userId: number;
  templateOverride?: string;
}

export interface GenerateDocumentResponse {
  documentUrl: string;
  preview: string;
  documentId: string;
  templateUsed: string;
  status: "success" | "partial" | "failed";
  warnings?: string[];
}

export interface CaseTypeMappingsResponse {
  mappings: Record<string, string[]>;
  lastUpdated: string;
}

export interface QuestionMappingsResponse {
  questions: string[];
  required: boolean[];
  fieldTypes: string[];
  validationRules: Record<string, any>;
}

export const legalCaseAPI = {
  // Process initial input (speech or text) to determine case type
  processInitialInput: (data: ProcessInitialInputRequest) =>
    api.post<ProcessInitialInputResponse>("/legal-case/process-input/", data),

  // Submit answer to a specific question
  submitAnswer: (data: SubmitAnswerRequest) =>
    api.post<SubmitAnswerResponse>("/legal-case/submit-answer/", data),

  // Generate final document
  generateDocument: (data: GenerateDocumentRequest) =>
    api.post<GenerateDocumentResponse>("/legal-case/generate-document/", data),

  // Get case type mappings (keywords to case types)
  getCaseTypeMappings: () =>
    api.get<CaseTypeMappingsResponse>("/legal-case/case-type-mappings/"),

  // Get questions for a specific case type
  getQuestionMappings: (caseType: string) =>
    api.get<QuestionMappingsResponse>(
      `/legal-case/question-mappings/${encodeURIComponent(caseType)}/`
    ),

  // Get available templates
  getAvailableTemplates: () => api.get("/legal-case/templates/"),

  // Preview document before final generation
  previewDocument: (data: GenerateDocumentRequest) =>
    api.post("/legal-case/preview-document/", data),

  // Get case processing status
  getCaseStatus: (caseId: string) => api.get(`/legal-case/status/${caseId}/`),

  // Update case with additional information
  updateCase: (caseId: string, data: any) =>
    api.put(`/legal-case/update/${caseId}/`, data),

  // Download generated document
  downloadDocument: (documentId: string) =>
    api.get(`/legal-case/download/${documentId}/`, {
      responseType: "blob",
    }),

  // Get case history for user
  getCaseHistory: (userId: number) => api.get(`/legal-case/history/${userId}/`),

  // Validate answers before document generation
  validateAnswers: (data: {
    caseType: string;
    answers: Record<string, string>;
  }) => api.post("/legal-case/validate-answers/", data),

  // Get legal guidance for a case type
  getLegalGuidance: (caseType: string) =>
    api.get(`/legal-case/guidance/${encodeURIComponent(caseType)}/`),

  // Submit feedback on generated document
  submitFeedback: (data: {
    documentId: string;
    rating: number;
    comments: string;
    improvements: string[];
  }) => api.post("/legal-case/feedback/", data),
};
