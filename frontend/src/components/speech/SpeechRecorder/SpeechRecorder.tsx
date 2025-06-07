// ============ src/components/speech/SpeechRecorder/SpeechRecorder.tsx ============
import React from "react";
import { IconButton, Box, Typography, CircularProgress } from "@mui/material";
import { Mic, MicOff, VolumeUp } from "@mui/icons-material";
import { useSpeech } from "../../../hooks/useSpeech";
import {
  StyledRecorderContainer,
  StyledRecordingIndicator,
} from "./SpeechRecorder.styles";

interface SpeechRecorderProps {
  onTranscriptionChange?: (text: string) => void;
  language?: string;
}

const SpeechRecorder: React.FC<SpeechRecorderProps> = ({
  onTranscriptionChange,
  language = "hi",
}) => {
  const {
    isRecording,
    isProcessing,
    transcription,
    startSpeechRecording,
    stopSpeechRecording,
    playTextAsAudio,
    audioUrl,
    playAudioUrl,
  } = useSpeech();

  React.useEffect(() => {
    if (transcription && onTranscriptionChange) {
      onTranscriptionChange(transcription);
    }
  }, [transcription, onTranscriptionChange]);

  React.useEffect(() => {
    if (audioUrl) {
      playAudioUrl(audioUrl);
    }
  }, [audioUrl, playAudioUrl]);

  const handleRecordClick = () => {
    if (isRecording) {
      stopSpeechRecording();
    } else {
      startSpeechRecording();
    }
  };

  const handlePlayback = () => {
    if (transcription) {
      playTextAsAudio(transcription);
    }
  };

  return (
    <StyledRecorderContainer>
      <Box display="flex" alignItems="center" gap={2}>
        <IconButton
          onClick={handleRecordClick}
          disabled={isProcessing}
          size="large"
          color={isRecording ? "secondary" : "primary"}
        >
          {isRecording ? <MicOff /> : <Mic />}
        </IconButton>

        {transcription && (
          <IconButton onClick={handlePlayback} disabled={isProcessing}>
            <VolumeUp />
          </IconButton>
        )}

        {isProcessing && <CircularProgress size={24} />}
      </Box>

      {isRecording && (
        <StyledRecordingIndicator>
          <Typography variant="body2" color="secondary">
            Recording... Speak clearly
          </Typography>
        </StyledRecordingIndicator>
      )}

      {transcription && (
        <Box mt={2}>
          <Typography variant="body2" color="textSecondary">
            Transcription:
          </Typography>
          <Typography variant="body1">{transcription}</Typography>
        </Box>
      )}
    </StyledRecorderContainer>
  );
};

export default SpeechRecorder;
