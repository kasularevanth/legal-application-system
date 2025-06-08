// src/hooks/useVoiceLegal.ts
import { useState, useCallback, useRef } from "react";
import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../store";
import { legalCaseAPI } from "../services/api/legalCase";
import { speechAPI } from "../services/api/speech";
import {
  processInitialInput,
  submitAnswer,
  generateDocument,
  updateStatus,
  setCurrentStep,
} from "../store/slices/legalCaseSlice";

interface VoiceRecordingState {
  isRecording: boolean;
  isProcessing: boolean;
  audioBlob: Blob | null;
  duration: number;
  error: string | null;
}

interface LegalCaseState {
  caseId: string | null;
  status: string;
  questions: string[];
  currentQuestionIndex: number;
  answers: Record<string, string>;
  caseType: string | null;
  confidence: number;
}

export const useVoiceLegal = () => {
  const dispatch = useDispatch();
  const legalCase = useSelector((state: RootState) => state.legalCase);

  // Voice recording state
  const [voiceState, setVoiceState] = useState<VoiceRecordingState>({
    isRecording: false,
    isProcessing: false,
    audioBlob: null,
    duration: 0,
    error: null,
  });

  // Refs for media recording
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioStreamRef = useRef<MediaStream | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const startTimeRef = useRef<number>(0);
  const durationIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Start voice recording
  const startRecording = useCallback(async (language: string = "hi") => {
    try {
      setVoiceState((prev) => ({ ...prev, error: null, duration: 0 }));

      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      audioStreamRef.current = stream;
      audioChunksRef.current = [];

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: "audio/webm;codecs=opus",
      });

      mediaRecorderRef.current = mediaRecorder;

      // Handle data available
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      // Handle recording stop
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/wav",
        });

        setVoiceState((prev) => ({
          ...prev,
          isRecording: false,
          isProcessing: true,
          audioBlob,
        }));

        // Process the audio
        await processVoiceInput(audioBlob, language);
      };

      // Start recording
      mediaRecorder.start();
      startTimeRef.current = Date.now();

      setVoiceState((prev) => ({ ...prev, isRecording: true }));

      // Start duration tracking
      durationIntervalRef.current = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000);
        setVoiceState((prev) => ({ ...prev, duration: elapsed }));
      }, 1000);
    } catch (error) {
      console.error("Failed to start recording:", error);
      setVoiceState((prev) => ({
        ...prev,
        error: "Failed to access microphone. Please check permissions.",
      }));
    }
  }, []);

  // Stop voice recording
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && voiceState.isRecording) {
      mediaRecorderRef.current.stop();
    }

    if (audioStreamRef.current) {
      audioStreamRef.current.getTracks().forEach((track) => track.stop());
      audioStreamRef.current = null;
    }

    if (durationIntervalRef.current) {
      clearInterval(durationIntervalRef.current);
      durationIntervalRef.current = null;
    }

    setVoiceState((prev) => ({ ...prev, isRecording: false }));
  }, [voiceState.isRecording]);

  // Process voice input for initial case creation
  const processVoiceInput = useCallback(
    async (audioBlob: Blob, language: string = "hi") => {
      try {
        setVoiceState((prev) => ({ ...prev, isProcessing: true }));
        dispatch(setCurrentStep("Processing voice input"));

        // Convert audio to FormData
        const formData = new FormData();
        formData.append("audio", audioBlob, "recording.wav");
        formData.append("language", language);

        // Send to backend for processing
        const response = await legalCaseAPI.processVoiceInput(formData);

        if (response.data.success) {
          // Update legal case state
          dispatch(
            processInitialInput.fulfilled({
              caseType: response.data.case_type,
              confidence: response.data.detection_confidence,
              keywords: response.data.detected_keywords,
              questions: response.data.questions,
              templateId: response.data.case_id,
              requiresQuestions: response.data.requires_questions,
            })
          );

          // Play voice prompt if available
          if (response.data.voice_prompt) {
            await playVoicePrompt(response.data.voice_prompt);
          }

          return {
            success: true,
            transcription: response.data.transcription,
            caseId: response.data.case_id,
            caseType: response.data.case_type,
            questions: response.data.questions,
          };
        } else {
          throw new Error(
            response.data.error || "Failed to process voice input"
          );
        }
      } catch (error) {
        console.error("Voice processing failed:", error);
        setVoiceState((prev) => ({
          ...prev,
          error: "Failed to process voice input. Please try again.",
        }));
        dispatch(updateStatus("error"));
        return { success: false, error: error.message };
      } finally {
        setVoiceState((prev) => ({ ...prev, isProcessing: false }));
      }
    },
    [dispatch]
  );

  // Answer question by voice
  const answerQuestionByVoice = useCallback(
    async (audioBlob: Blob, caseId: string, language: string = "hi") => {
      try {
        setVoiceState((prev) => ({ ...prev, isProcessing: true }));
        dispatch(setCurrentStep("Processing answer"));

        const formData = new FormData();
        formData.append("audio", audioBlob, "answer.wav");
        formData.append("case_id", caseId);
        formData.append("language", language);

        const response = await legalCaseAPI.answerQuestionByVoice(formData);

        if (response.data.success) {
          // Update store with answer
          dispatch(
            submitAnswer.fulfilled({
              questionIndex: legalCase.currentQuestionIndex,
              answer: response.data.validated_answer,
              nextQuestion: !response.data.questioning_complete,
            })
          );

          // Play next question prompt if available
          if (
            response.data.voice_prompt &&
            !response.data.questioning_complete
          ) {
            await playVoicePrompt(response.data.voice_prompt);
          }

          // If questioning complete, trigger document generation
          if (response.data.questioning_complete) {
            setTimeout(() => {
              generateLegalDocument(caseId);
            }, 1000);
          }

          return {
            success: true,
            answer: response.data.validated_answer,
            questioningComplete: response.data.questioning_complete,
            nextQuestion: response.data.next_question,
          };
        } else {
          throw new Error(response.data.error || "Failed to process answer");
        }
      } catch (error) {
        console.error("Answer processing failed:", error);
        setVoiceState((prev) => ({
          ...prev,
          error: "Failed to process answer. Please try again.",
        }));
        return { success: false, error: error.message };
      } finally {
        setVoiceState((prev) => ({ ...prev, isProcessing: false }));
      }
    },
    [dispatch, legalCase.currentQuestionIndex]
  );

  // Generate legal document
  const generateLegalDocument = useCallback(
    async (caseId: string) => {
      try {
        dispatch(updateStatus("generating"));
        dispatch(setCurrentStep("Generating legal document"));

        const response = await legalCaseAPI.generateDocument({
          case_id: caseId,
        });

        if (response.data.success) {
          dispatch(
            generateDocument.fulfilled({
              documentUrl: response.data.document_url,
              preview: response.data.preview,
              documentId: response.data.document_id,
              templateUsed: response.data.template_used,
            })
          );

          return {
            success: true,
            documentUrl: response.data.document_url,
            documentId: response.data.document_id,
          };
        } else {
          throw new Error(response.data.error || "Failed to generate document");
        }
      } catch (error) {
        console.error("Document generation failed:", error);
        dispatch(updateStatus("error"));
        return { success: false, error: error.message };
      }
    },
    [dispatch]
  );

  // Play voice prompt
  const playVoicePrompt = useCallback(
    async (text: string, language: string = "hi") => {
      try {
        const response = await speechAPI.textToSpeech({
          text,
          language,
        });

        if (response.data.audio_url) {
          const audio = new Audio(response.data.audio_url);
          await audio.play();
        }
      } catch (error) {
        console.warn("Failed to play voice prompt:", error);
        // Non-critical error, don't throw
      }
    },
    []
  );

  // Convert text to speech for guidance
  const speakText = useCallback(
    async (
      text: string,
      language: string = "hi",
      type: "general" | "question" | "instruction" = "general"
    ) => {
      try {
        const response = await speechAPI.generateVoiceGuidance({
          text,
          language,
          type,
        });

        if (response.data.success && response.data.audio_url) {
          const audio = new Audio(response.data.audio_url);
          await audio.play();
          return true;
        }
        return false;
      } catch (error) {
        console.error("Text to speech failed:", error);
        return false;
      }
    },
    []
  );

  // Get case status
  const getCaseStatus = useCallback(async (caseId: string) => {
    try {
      const response = await legalCaseAPI.getCaseStatus(caseId);
      return response.data;
    } catch (error) {
      console.error("Failed to get case status:", error);
      return null;
    }
  }, []);

  // Reset voice state
  const resetVoiceState = useCallback(() => {
    // Stop any ongoing recording
    if (voiceState.isRecording) {
      stopRecording();
    }

    // Clear intervals
    if (durationIntervalRef.current) {
      clearInterval(durationIntervalRef.current);
      durationIntervalRef.current = null;
    }

    // Reset state
    setVoiceState({
      isRecording: false,
      isProcessing: false,
      audioBlob: null,
      duration: 0,
      error: null,
    });
  }, [voiceState.isRecording, stopRecording]);

  // Cleanup on unmount
  const cleanup = useCallback(() => {
    resetVoiceState();

    if (audioStreamRef.current) {
      audioStreamRef.current.getTracks().forEach((track) => track.stop());
      audioStreamRef.current = null;
    }
  }, [resetVoiceState]);

  return {
    // Voice recording state
    voiceState,

    // Legal case state from Redux
    legalCase,

    // Voice recording methods
    startRecording,
    stopRecording,
    resetVoiceState,

    // Legal processing methods
    processVoiceInput,
    answerQuestionByVoice,
    generateLegalDocument,

    // Utility methods
    speakText,
    playVoicePrompt,
    getCaseStatus,
    cleanup,

    // Computed values
    canRecord: !voiceState.isRecording && !voiceState.isProcessing,
    hasAudio: !!voiceState.audioBlob,
    recordingDuration: voiceState.duration,
    currentQuestion: legalCase.questions[legalCase.currentQuestionIndex],
    isQuestioningComplete:
      legalCase.currentQuestionIndex >= legalCase.questions.length,
  };
};
