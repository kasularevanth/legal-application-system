// ============ frontend/src/components/voice/EnhancedVoiceInput/EnhancedVoiceInput.tsx ============
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  IconButton,
  LinearProgress,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Fab,
  Tooltip,
  Fade,
  Collapse,
} from '@mui/material';
import {
  Mic,
  MicOff,
  Stop,
  PlayArrow,
  Refresh,
  VolumeUp,
  Edit,
  CheckCircle,
  Error as ErrorIcon,
  Info,
  QuestionAnswer,
} from '@mui/icons-material';
import { styled, keyframes } from '@mui/material/styles';
import { useVoiceLegalProcessing } from '../../../hooks/useVoiceLegalProcessing';
import { useTranslation } from 'react-i18next';

// Styled components with animations
const pulse = keyframes`
  0% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(25, 118, 210, 0.7);
  }
  70% {
    transform: scale(1.05);
    box-shadow: 0 0 0 10px rgba(25, 118, 210, 0);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(25, 118, 210, 0);
  }
`;

const RecordingButton = styled(Fab)<{ recording?: boolean }>(({ theme, recording }) => ({
  width: 80,
  height: 80,
  animation: recording ? `${pulse} 2s infinite` : 'none',
  transition: 'all 0.3s ease-in-out',
  background: recording
    ? `linear-gradient(45deg, ${theme.palette.error.main} 30%, ${theme.palette.error.dark} 90%)`
    : `linear-gradient(45deg, ${theme.palette.primary.main} 30%, ${theme.palette.primary.dark} 90%)`,
}));

const StageIndicator = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
  padding: theme.spacing(1),
  borderRadius: theme.shape.borderRadius,
  backgroundColor: theme.palette.action.hover,
  marginBottom: theme.spacing(2),
}));

const TranscriptionBox = styled(Card)(({ theme }) => ({
  marginTop: theme.spacing(2),
  padding: theme.spacing(2),
  backgroundColor: theme.palette.background.paper,
  border: `1px solid ${theme.palette.divider}`,
  borderRadius: theme.shape.borderRadius * 2,
}));

const AnalysisCard = styled(Card)(({ theme }) => ({
  marginTop: theme.spacing(2),
  background: `linear-gradient(135deg, ${theme.palette.primary.light}15 0%, ${theme.palette.secondary.light}15 100%)`,
  border: `1px solid ${theme.palette.primary.light}`,
}));

interface EnhancedVoiceInputProps {
  onCaseCreated?: (caseData: any) => void;
  onAnalysisComplete?: (analysis: any) => void;
}

const EnhancedVoiceInput: React.FC<EnhancedVoiceInputProps> = ({
  onCaseCreated,
  onAnalysisComplete,
}) => {
  const { t } = useTranslation();
  const {
    isRecording,
    isProcessing,
    currentStage,
    progress,
    transcription,
    caseAnalysis,
    error,
    caseId,
    startRecording,
    stopRecording,
    resetSession,
    addMoreInformation,
    isWebSocketConnected,
  } = useVoiceLegalProcessing();

  const [showAdditionalInfoDialog, setShowAdditionalInfoDialog] = useState(false);
  const [additionalInfo, setAdditionalInfo] = useState('');
  const [activeStep, setActiveStep] = useState(0);
  const [showFullAnalysis, setShowFullAnalysis] = useState(false);

  // Processing stages for stepper
  const stages = [
    { key: 'idle', label: 'Ready to Record', icon: <Mic /> },
    { key: 'recording', label: 'Recording Voice', icon: <MicOff /> },
    { key: 'processing_audio', label: 'Processing Audio', icon: <VolumeUp /> },
    { key: 'transcribing', label: 'Converting to Text', icon: <Edit /> },
    { key: 'analyzing', label: 'Analyzing Legal Context', icon: <QuestionAnswer /> },
    { key: 'completed', label: 'Analysis Complete', icon: <CheckCircle /> },
  ];

  // Update active step based on current stage
  useEffect(() => {
    const stageIndex = stages.findIndex(stage => stage.key === currentStage);
    if (stageIndex !== -1) {
      setActiveStep(stageIndex);
    }
  }, [currentStage]);

  // Call callbacks when analysis is complete
  useEffect(() => {
    if (caseAnalysis && onAnalysisComplete) {
      onAnalysisComplete(caseAnalysis);
    }
  }, [caseAnalysis, onAnalysisComplete]);

  useEffect(() => {
    if (caseId && onCaseCreated) {
      onCaseCreated({ caseId, analysis: caseAnalysis });
    }
  }, [caseId, caseAnalysis, onCaseCreated]);

  const handleToggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const handleAddMoreInfo = async () => {
    if (additionalInfo.trim()) {
      try {
        await addMoreInformation(additionalInfo.trim());
        setAdditionalInfo('');
        setShowAdditionalInfoDialog(false);
      } catch (error) {
        console.error('Failed to add additional information:', error);
      }
    }
  };

  const getStageMessage = (stage: string): string => {
    const messages: Record<string, string> = {
      idle: 'Ready to record your legal issue',
      requesting_permission: 'Requesting microphone access...',
      recording: 'Listening... Speak clearly about your legal issue',
      processing_audio: 'Processing your voice recording...',
      transcribing: 'Converting speech to text...',
      analyzing: 'Analyzing legal context and case type...',
      analysis_detecting_type: 'Detecting case type...',
      analysis_extracting_entities: 'Extracting legal entities...',
      analysis_generating_suggestions: 'Generating legal suggestions...',
      completed: 'Voice analysis completed successfully!',
      error: 'An error occurred during processing',
    };
    return messages[stage] || stage;
  };

  const getConfidenceColor = (confidence: number): 'success' | 'warning' | 'error' => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const formatCaseType = (caseType: string): string => {
    return caseType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 2 }}>
      {/* Connection Status */}
      {!isWebSocketConnected && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Real-time updates disconnected. Some features may be limited.
        </Alert>
      )}

      {/* Error Display */}
      {error && (
        <Alert 
          severity="error" 
          sx={{ mb: 2 }}
          action={
            <Button color="inherit" size="small" onClick={resetSession}>
              Try Again
            </Button>
          }
        >
          {error}
        </Alert>
      )}

      {/* Main Voice Input Card */}
      <Card elevation={3}>
        <CardContent sx={{ p: 4 }}>
          {/* Current Stage Indicator */}
          <StageIndicator>
            <Info color="primary" />
            <Typography variant="body2">
              {getStageMessage(currentStage)}
            </Typography>
            {isWebSocketConnected && (
              <Chip 
                label="Live" 
                color="success" 
                size="small" 
                sx={{ ml: 'auto' }}
              />
            )}
          </StageIndicator>

          {/* Progress Bar */}
          {isProcessing && (
            <Box sx={{ mb: 3 }}>
              <LinearProgress 
                variant="determinate" 
                value={progress} 
                sx={{ height: 8, borderRadius: 4 }}
              />
              <Typography variant="caption" color="textSecondary" sx={{ mt: 1 }}>
                {progress}% Complete
              </Typography>
            </Box>
          )}

          {/* Recording Button */}
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
            <Tooltip title={isRecording ? 'Stop Recording' : 'Start Recording'}>
              <RecordingButton
                recording={isRecording}
                onClick={handleToggleRecording}
                disabled={isProcessing}
                color={isRecording ? 'error' : 'primary'}
              >
                {isRecording ? <Stop sx={{ fontSize: 32 }} /> : <Mic sx={{ fontSize: 32 }} />}
              </RecordingButton>
            </Tooltip>
          </Box>

          {/* Processing Stepper */}
          {(isProcessing || transcription) && (
            <Fade in timeout={500}>
              <Box sx={{ mb: 3 }}>
                <Stepper activeStep={activeStep} orientation="vertical">
                  {stages.map((stage, index) => (
                    <Step key={stage.key} completed={index < activeStep}>
                      <StepLabel
                        StepIconComponent={() => (
                          <Box
                            sx={{
                              width: 24,
                              height: 24,
                              borderRadius: '50%',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              backgroundColor: index <= activeStep ? 'primary.main' : 'grey.300',
                              color: 'white',
                            }}
                          >
                            {React.cloneElement(stage.icon, { sx: { fontSize: 16 } })}
                          </Box>
                        )}
                      >
                        <Typography variant="body2">{stage.label}</Typography>
                      </StepLabel>
                    </Step>
                  ))}
                </Stepper>
              </Box>
            </Fade>
          )}

          {/* Action Buttons */}
          <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center', flexWrap: 'wrap' }}>
            {transcription && !isProcessing && (
              <>
                <Button
                  variant="outlined"
                  startIcon={<QuestionAnswer />}
                  onClick={() => setShowAdditionalInfoDialog(true)}
                  disabled={!caseId}
                >
                  Add More Info
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={resetSession}
                >
                  Start Over
                </Button>
              </>
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Transcription Display */}
      {transcription && (
        <Collapse in timeout={500}>
          <TranscriptionBox>
            <Typography variant="h6" gutterBottom>
              Transcription
            </Typography>
            <Typography variant="body1" sx={{ fontStyle: 'italic', lineHeight: 1.6 }}>
              "{transcription}"
            </Typography>
          </TranscriptionBox>
        </Collapse>
      )}

      {/* Case Analysis Display */}
      {caseAnalysis && (
        <Collapse in timeout={800}>
          <AnalysisCard>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Legal Analysis</Typography>
                <Button
                  size="small"
                  onClick={() => setShowFullAnalysis(!showFullAnalysis)}
                >
                  {showFullAnalysis ? 'Show Less' : 'Show More'}
                </Button>
              </Box>

              {/* Basic Analysis */}
              <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
                {caseAnalysis.case_analysis && (
                  <>
                    <Chip
                      label={`Type: ${formatCaseType(caseAnalysis.case_analysis.primary_case_type)}`}
                      color="primary"
                      variant="outlined"
                    />
                    <Chip
                      label={`Confidence: ${Math.round((caseAnalysis.case_analysis.confidence_score || 0) * 100)}%`}
                      color={getConfidenceColor(caseAnalysis.case_analysis.confidence_score || 0)}
                      variant="outlined"
                    />
                    <Chip
                      label={`Complexity: ${caseAnalysis.case_analysis.legal_complexity || 'Unknown'}`}
                      variant="outlined"
                    />
                  </>
                )}
              </Box>

              {/* Expanded Analysis */}
              <Collapse in={showFullAnalysis}>
                <Box sx={{ mt: 2 }}>
                  {caseAnalysis.extracted_information?.key_facts && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Key Facts Identified:
                      </Typography>
                      {caseAnalysis.extracted_information.key_facts.map((fact: string, index: number) => (
                        <Typography key={index} variant="body2" sx={{ ml: 2, mb: 0.5 }}>
                          • {fact}
                        </Typography>
                      ))}
                    </Box>
                  )}

                  {caseAnalysis.suggested_improvements?.immediate_clarifications && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Suggested Clarifications:
                      </Typography>
                      {caseAnalysis.suggested_improvements.immediate_clarifications.map((question: string, index: number) => (
                        <Typography key={index} variant="body2" sx={{ ml: 2, mb: 0.5 }}>
                          • {question}
                        </Typography>
                      ))}
                    </Box>
                  )}

                  {caseAnalysis.next_steps?.immediate_actions && (
                    <Box>
                      <Typography variant="subtitle2" gutterBottom>
                        Recommended Next Steps:
                      </Typography>
                      {caseAnalysis.next_steps.immediate_actions.map((action: string, index: number) => (
                        <Typography key={index} variant="body2" sx={{ ml: 2, mb: 0.5 }}>
                          • {action}
                        </Typography>
                      ))}
                    </Box>
                  )}
                </Box>
              </Collapse>
            </CardContent>
          </AnalysisCard>
        </Collapse>
      )}

      {/* Additional Information Dialog */}
      <Dialog
        open={showAdditionalInfoDialog}
        onClose={() => setShowAdditionalInfoDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Add More Information</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
            You can provide additional details about your legal case to improve the analysis.
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={4}
            value={additionalInfo}
            onChange={(e) => setAdditionalInfo(e.target.value)}
            placeholder="Provide any additional details about your case..."
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowAdditionalInfoDialog(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleAddMoreInfo}
            variant="contained"
            disabled={!additionalInfo.trim()}
          >
            Add Information
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EnhancedVoiceInput;
