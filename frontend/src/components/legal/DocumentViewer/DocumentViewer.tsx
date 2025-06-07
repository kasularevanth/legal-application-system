import React from 'react';
import { Box, Typography, Paper, Link } from '@mui/material';
import { PictureAsPdf, Description } from '@mui/icons-material'; // Example icons

interface DocumentViewerProps {
  documentUrl: string;
  title?: string;
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({ documentUrl, title = "View Document" }) => {
  const isPdf = documentUrl.toLowerCase().endsWith('.pdf');

  return (
    <Paper elevation={3} sx={{ p: 3, mt: 2 }}>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <Box display="flex" alignItems="center" sx={{ mb: 2 }}>
        {isPdf ? <PictureAsPdf sx={{ mr: 1 }} /> : <Description sx={{ mr: 1 }} />}
        <Typography variant="body1">
          Document: <Link href={documentUrl} target="_blank" rel="noopener noreferrer">Open Document</Link>
        </Typography>
      </Box>
      {isPdf ? (
        <Box
          component="iframe"
          src={documentUrl}
          title={title}
          sx={{
            width: '100%',
            height: '500px', // Adjust height as needed
            border: '1px solid #ccc',
          }}
        />
      ) : (
        <Typography variant="body2" color="textSecondary">
          Preview for non-PDF documents is not available. Please open the document using the link above.
        </Typography>
      )}
    </Paper>
  );
};

export default DocumentViewer;
