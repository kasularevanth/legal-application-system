




// ============ frontend/src/pages/DocumentGeneration/DocumentGeneration.tsx (New) ============
import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Grid,
  Chip,
  Alert,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Description,
  Download,
  Preview,
  CheckCircle,
  Error as ErrorIcon,
  Gavel,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { useWebSocket } from '../../hooks/useWebSocket';
import { voiceLegalAPI } from '../../services/api/voiceLegal';

const DocumentGeneration: React.FC = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const webSocket = useWebSocket();
  
  const [caseDetails, setCaseDetails] = useState<any>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedDocuments, setGeneratedDocuments] = useState<any[]>([]);
  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [previewDocument, setPreviewDocument] = useState<any>(null);

  useEffect(() => {
    if (caseId) {
      loadCaseDetails();
      
      // Subscribe to document generation updates
      if (webSocket.isConnected) {
        webSocket.subscribeToCase(caseId);
        webSocket.onDocumentGeneration((update) => {
          setProgress(update.progress);
          setCurrentStage(update.stage);
          
          if (update.stage === 'completed') {
            setIsGenerating(false);
            loadGeneratedDocuments();
          }
        });
      }
    }

    return () => {
      if (caseId && webSocket.isConnected) {
        webSocket.unsubscribeFromCase(caseId);
      }
    };
  }, [caseId, webSocket]);

  const loadCaseDetails = async () => {
    try {
      const response = await voiceLegalAPI.getCaseDetails(caseId!);
      setCaseDetails(response);
    } catch (error) {
      console.error('Failed to load case details:', error);
      setError('Failed to load case details');
    }
  };

  const loadGeneratedDocuments = async () => {
    try {
      const response = await voiceLegalAPI.getGeneratedDocuments(caseId!);
      setGeneratedDocuments(response);
    } catch (error) {
      console.error('Failed to load generated documents:', error);
    }
  };

  const handleGenerateDocuments = async () => {
    try {
      setIsGenerating(true);
      setError(null);
      setProgress(0);
      
      await voiceLegalAPI.generateDocuments(caseId!);
      
      // Progress will be updated via WebSocket
    } catch (error) {
      console.error('Failed to generate documents:', error);
      setError('Failed to generate documents');
      setIsGenerating(false);
    }
  };

  const handleDownloadDocument = async (documentId: string) => {
    try {
      const response = await voiceLegalAPI.downloadDocument(documentId);
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `document_${documentId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download document:', error);
    }
  };

  const handlePreviewDocument = (document: any) => {
    setPreviewDocument(document);
  };

  if (!caseDetails) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <LinearProgress />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Loading case details...
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Document Generation
        </Typography>
        <Typography variant="subtitle1" color="textSecondary">
          Generate legal documents for your case
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Case Summary */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Case Summary
              </Typography>
              
              {caseDetails.analysis?.case_analysis && (
                <Box sx={{ mb: 2 }}>
                  <Chip
                    label={`Type: ${caseDetails.analysis.case_analysis.primary_case_type}`}
                    color="primary"
                    sx={{ mr: 1, mb: 1 }}
                  />
                  <Chip
                    label={`Confidence: ${Math.round((caseDetails.analysis.case_analysis.confidence_score || 0) * 100)}%`}
                    color="success"
                    sx={{ mr: 1, mb: 1 }}
                  />
                </Box>
              )}

              {caseDetails.transcription && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Voice Input:
                  </Typography>
                  <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                    "{caseDetails.transcription}"
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Document Generation */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Generate Documents
              </Typography>

              {isGenerating && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" gutterBottom>
                    {currentStage || 'Generating documents...'}
                  </Typography>
                  <LinearProgress variant="determinate" value={progress} />
                  <Typography variant="caption" color="textSecondary">
                    {progress}% Complete
                  </Typography>
                </Box>
              )}

              <Button
                variant="contained"
                startIcon={<Description />}
                onClick={handleGenerateDocuments}
                disabled={isGenerating}
                fullWidth
                size="large"
              >
                {isGenerating ? 'Generating...' : 'Generate Legal Documents'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Generated Documents */}
        {generatedDocuments.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Generated Documents
                </Typography>
                
                <List>
                  {generatedDocuments.map((document) => (
                    <ListItem
                      key={document.id}
                      sx={{
                        border: 1,
                        borderColor: 'divider',
                        borderRadius: 1,
                        mb: 1,
                      }}
                    >
                      <ListItemIcon>
                        <Gavel color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={document.document_type}
                        secondary={`Generated on ${new Date(document.created_at).toLocaleDateString()}`}
                      />
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button
                          size="small"
                          startIcon={<Preview />}
                          onClick={() => handlePreviewDocument(document)}
                        >
                          Preview
                        </Button>
                        <Button
                          size="small"
                          startIcon={<Download />}
                          onClick={() => handleDownloadDocument(document.id)}
                        >
                          Download
                        </Button>
                      </Box>
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>

      {/* Document Preview Dialog */}
      <Dialog
        open={!!previewDocument}
        onClose={() => setPreviewDocument(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Document Preview - {previewDocument?.document_type}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2">
            Document preview functionality would be implemented here.
            This could include PDF viewer or HTML preview.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewDocument(null)}>
            Close
          </Button>
          <Button
            variant="contained"
            startIcon={<Download />}
            onClick={() => handleDownloadDocument(previewDocument?.id)}
          >
            Download
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};


export default DocumentGeneration;