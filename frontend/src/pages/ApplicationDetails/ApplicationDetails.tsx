import React, { useEffect } from 'react';
import { Container, Typography, Box, Paper, CircularProgress, Alert, Button } from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../store';
import { fetchApplicationDetails } from '../../store/slices/formsSlice';
import DocumentViewer from '../../components/legal/DocumentViewer'; // Assuming this component will be fixed/created

const ApplicationDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const { currentApplication: application, loading, error } = useSelector(
    (state: RootState) => state.forms
  );

  useEffect(() => {
    if (id) {
      dispatch(fetchApplicationDetails(parseInt(id)) as any);
    }
  }, [dispatch, id]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">Error loading application details: {error}</Alert>;
  }

  if (!application) {
    return <Alert severity="warning">Application not found.</Alert>;
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          {application.title || `Application #${application.id}`}
        </Typography>
        <Typography variant="subtitle1" color="textSecondary" gutterBottom>
          Status: {application.status}
        </Typography>
        <Typography variant="body1" paragraph>
          Submitted on: {new Date(application.created_at).toLocaleDateString()}
        </Typography>
        {/* Add more application details here */}
      </Paper>

      {application.generated_document_url && (
        <DocumentViewer documentUrl={application.generated_document_url} />
      )}

      <Box mt={3}>
        <Button variant="outlined" onClick={() => navigate('/dashboard')}>
          Back to Dashboard
        </Button>
      </Box>
    </Container>
  );
};

export default ApplicationDetails;
