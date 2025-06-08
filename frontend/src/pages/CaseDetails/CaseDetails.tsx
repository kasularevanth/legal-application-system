

// ============ frontend/src/pages/CaseDetails/CaseDetails.tsx (New) ============
import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  Alert,
} from '@mui/material';
import {
  VoiceChat,
  Description,
  Download,
  Edit,
  Share,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { voiceLegalAPI } from '../../services/api/voiceLegal';

const CaseDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [caseData, setCaseData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadCaseDetails();
    }
  }, [id]);

  const loadCaseDetails = async () => {
    try {
      const response = await voiceLegalAPI.getCaseDetails(id!);
      setCaseData(response);
    } catch (error) {
      console.error('Failed to load case details:', error);
      setError('Failed to load case details');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography>Loading case details...</Typography>
      </Container>
    );
  }

  if (error || !caseData) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">{error || 'Case not found'}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Case Details
        </Typography>
        <Typography variant="subtitle1" color="textSecondary">
          Case ID: {caseData.case_id}
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Case Overview */}
        <Grid item xs={12} md={8}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Case Overview
              </Typography>
              
              {caseData.analysis?.case_analysis && (
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                    <Chip
                      label={`Type: ${caseData.analysis.case_analysis.primary_case_type}`}
                      color="primary"
                    />
                    <Chip
                      label={`Confidence: ${Math.round((caseData.analysis.case_analysis.confidence_score || 0) * 100)}%`}
                      color="success"
                    />
                    <Chip
                      label={`Status: ${caseData.status}`}
                      color="info"
                    />
                  </Box>
                </Box>
              )}

              {caseData.transcription && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Original Voice Input:
                  </Typography>
                  <Typography variant="body2" sx={{ fontStyle: 'italic', p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                    "{caseData.transcription}"
                  </Typography>
                </Box>
              )}

              {caseData.analysis?.extracted_information?.key_facts && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Key Facts:
                  </Typography>
                  {caseData.analysis.extracted_information.key_facts.map((fact: string, index: number) => (
                    <Typography key={index} variant="body2" sx={{ ml: 2 }}>
                      • {fact}
                    </Typography>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>

          {/* Case Timeline */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Case Timeline
              </Typography>
              
              <Timeline>
                <TimelineItem>
                  <TimelineSeparator>
                    <TimelineDot color="primary">
                      <VoiceChat />
                    </TimelineDot>
                    <TimelineConnector />
                  </TimelineSeparator>
                  <TimelineContent>
                    <Typography variant="subtitle2">
                      Voice Input Recorded
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {new Date(caseData.created_at).toLocaleString()}
                    </Typography>
                  </TimelineContent>
                </TimelineItem>

                <TimelineItem>
                  <TimelineSeparator>
                    <TimelineDot color="success">
                      <Description />
                    </TimelineDot>
                    {caseData.documents?.length > 0 && <TimelineConnector />}
                  </TimelineSeparator>
                  <TimelineContent>
                    <Typography variant="subtitle2">
                      AI Analysis Completed
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Case type detected and analyzed
                    </Typography>
                  </TimelineContent>
                </TimelineItem>

                {caseData.documents?.length > 0 && (
                  <TimelineItem>
                    <TimelineSeparator>
                      <TimelineDot color="info">
                        <Download />
                      </TimelineDot>
                    </TimelineSeparator>
                    <TimelineContent>
                      <Typography variant="subtitle2">
                        Documents Generated
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {caseData.documents.length} document(s) created
                      </Typography>
                    </TimelineContent>
                  </TimelineItem>
                )}
              </Timeline>
            </CardContent>
          </Card>
        </Grid>

        {/* Actions Sidebar */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Actions
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<Description />}
                  onClick={() => navigate(`/generate-documents/${id}`)}
                  fullWidth
                >
                  Generate Documents
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<Edit />}
                  onClick={() => navigate(`/voice-assistant?case=${id}`)}
                  fullWidth
                >
                  Add More Information
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<Share />}
                  fullWidth
                >
                  Share Case
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<Download />}
                  fullWidth
                >
                  Export Case Data
                </Button>
              </Box>
            </CardContent>
          </Card>

          {/* Case Statistics */}
          {caseData.analysis && (
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Analysis Details
                </Typography>
                
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Complexity:</Typography>
                    <Typography variant="body2" color="primary">
                      {caseData.analysis.case_analysis?.legal_complexity || 'Unknown'}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Urgency:</Typography>
                    <Typography variant="body2" color="warning.main">
                      {caseData.analysis.case_analysis?.urgency_level || 'Normal'}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Voice Quality:</Typography>
                    <Typography variant="body2" color="success.main">
                      {Math.round((caseData.analysis.voice_quality_assessment?.clarity_score || 0) * 100)}%
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Container>
  );
};

export default CaseDetails;
