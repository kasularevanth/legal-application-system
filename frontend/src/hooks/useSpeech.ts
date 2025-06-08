// ============ src/hooks/useSpeech.ts ============
import { useState, useCallback, useRef } from "react";
import { useDispatch, useSelector } from "react-redux";
import { RootState, AppDispatch } from "../store";
import {
  startRecording,
  stopRecording,
  setTranscription,
  speechToText,
  textToSpeech,
} from "../store/slices/speechSlice";

export const useSpeech = () => {
  const dispatch = useDispatch<AppDispatch>();
  const {
    isRecording,
    isProcessing,
    transcription,
    language,
    audioUrl,
    error,
  } = useSelector((state: RootState) => state.speech);

  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(
    null
  );
  const [audioStream, setAudioStream] = useState<MediaStream | null>(null);
  const audioChunks = useRef<Blob[]>([]);

  const startSpeechRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
        },
      });

      setAudioStream(stream);

      const recorder = new MediaRecorder(stream, {
        mimeType: "audio/webm;codecs=opus",
      });

      audioChunks.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks.current, { type: "audio/wav" });
        const audioFile = new File([audioBlob], "recording.wav", {
          type: "audio/wav",
        });

        // Convert to text using backend
        dispatch(speechToText({ file: audioFile, language }));
      };

      setMediaRecorder(recorder);
      recorder.start();
      dispatch(startRecording());
    } catch (error) {
      console.error("Error starting recording:", error);
    }
  }, [dispatch, language]);

  const stopSpeechRecording = useCallback(() => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
      dispatch(stopRecording());
    }

    if (audioStream) {
      audioStream.getTracks().forEach((track) => track.stop());
      setAudioStream(null);
    }
  }, [mediaRecorder, audioStream, dispatch]);

  const playTextAsAudio = useCallback(
    (text: string) => {
      dispatch(textToSpeech({ text, language }));
    },
    [dispatch, language]
  );

  const playAudioUrl = useCallback((url: string) => {
    const audio = new Audio(url);
    audio.play().catch(console.error);
  }, []);

  return {
    isRecording,
    isProcessing,
    transcription,
    language,
    audioUrl,
    error,
    startSpeechRecording,
    stopSpeechRecording,
    playTextAsAudio,
    playAudioUrl,
    setTranscription: (text: string) => dispatch(setTranscription(text)),
  };
};
