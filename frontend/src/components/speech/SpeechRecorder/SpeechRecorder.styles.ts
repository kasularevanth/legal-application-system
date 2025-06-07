// ============ src/components/speech/SpeechRecorder/SpeechRecorder.styles.ts ============
import styled from "styled-components";
import { Box } from "@mui/material";

export const StyledRecorderContainer = styled(Box)`
  padding: 16px;
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
  text-align: center;
  background-color: #fafafa;

  &:hover {
    border-color: var(--primary-color);
  }
`;

export const StyledRecordingIndicator = styled.div`
  margin-top: 8px;
  padding: 8px;
  background-color: rgba(220, 0, 78, 0.1);
  border-radius: 4px;
  animation: pulse 1.5s infinite;
`;
