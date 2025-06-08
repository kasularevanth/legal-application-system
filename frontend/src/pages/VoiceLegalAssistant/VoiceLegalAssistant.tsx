


// ============ frontend/src/pages/VoiceLegalAssistant/VoiceLegalAssistant.tsx (Enhanced) ============
import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Button,
  Alert,
  Stepper,
  Step,
  StepLabel,
  StepContent,
} from '@mui/material';
import {
  VoiceChat,
  Description,
  CloudDownload,
  Share,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import EnhancedVoiceInput from '../../components/voice/EnhancedVoiceInput';
import { useWebSocket } from '../../hooks/useWebSocket';

const VoiceLegalAssistant: React.FC = () => {
  const navigate = useNavigate();
  const webSocket = useWebSocket();
  const [currentCase, setCurrentCase] = useState<any>(null);
  const [activeStep, setActiveStep] = useState(0);

  const steps = [
    {
      label: 'Record Your Legal Issue',
      description: 'Speak clearly about your legal problem',
      icon: <VoiceChat />,
    },
    {
      label: 'Review Analysis',
      description: 'Check the AI analysis of your case',
      icon: <Description />,
    },
    {
      label: 'Generate Documents',
      description: 'Create legal documents based on your case',
      icon: <CloudDownload />,
    },
  ];

  const handleCaseCreated = (caseData: any) => {
    setCurrentCase(caseData);
    if (webSocket.isConnected) {
      webSocket.subscribeToCase(caseData.caseId);
    }
  };

  const handleAnalysisComplete = (analysis: any) => {
    setActiveStep(1);
  };

  const handleGenerateDocuments = () => {
    if (currentCase?.caseId) {
      navigate(`/generate-documents/${currentCase.caseId}`);
    }
  };

  const handleViewCase = () => {
    if (currentCase?.caseId) {
      navigate(`/cases/${currentCase.caseId}`);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Voice Legal Assistant
        </Typography>
        <Typography variant="h6" color="textSecondary" paragraph>
          Speak your legal issue and get instant AI-powered analysis and document generation
        </Typography>
      </Box>

      <Grid container spacing={4}>
        {/* Main Voice Input */}
        <Grid item xs={12} lg={8}>
          <EnhancedVoiceInput
            onCaseCreated={handleCaseCreated}
            onAnalysisComplete={handleAnalysisComplete}
          />
        </Grid>

        {/* Process Steps & Actions */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Process Steps
              </Typography>
              
              <Stepper activeStep={activeStep} orientation="vertical">
                {steps.map((step, index) => (
                  <Step key={step.label}>
                    <StepLabel
                      StepIconComponent={() => (
                        <Box
                          sx={{
                            width: 40,
                            height: 40,
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            backgroundColor: index <= activeStep ? 'primary.main' : 'grey.300',
                            color: 'white',
                          }}
                        >
                          {step.icon}
                        </Box>
                      )}
                    >
                      {step.label}
                    </StepLabel>
                    <StepContent>
                      <Typography variant="body2" color="textSecondary">
                        {step.description}
                      </Typography>
                    </StepContent>
                  </Step>
                ))}
              </Stepper>

              {/* Action Buttons */}
              {currentCase && (
                <Box sx={{ mt: 3, display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Button
                    variant="contained"
                    startIcon={<Description />}
                    onClick={handleGenerateDocuments}
                    fullWidth
                  >
                    Generate Documents
                  </Button>
                  
                  <Button
                    variant="outlined"
                    onClick={handleViewCase}
                    fullWidth
                  >
                    View Full Case Details
                  </Button>
                </Box>
              )}

              {/* Connection Status */}
              <Box sx={{ mt: 3 }}>
                <Alert 
                  severity={webSocket.isConnected ? 'success' : 'warning'}
                  variant="outlined"
                >
                  {webSocket.isConnected ? 'Real-time updates connected' : 'Real-time updates disconnected'}
                </Alert>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default VoiceLegalAssistant;