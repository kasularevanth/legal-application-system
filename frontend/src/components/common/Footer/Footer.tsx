import React from 'react';
import { Box, Container, Typography, Link as MuiLink } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const Footer: React.FC = () => {
  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 'auto', // Pushes footer to the bottom
        backgroundColor: (theme) =>
          theme.palette.mode === 'light'
            ? theme.palette.grey[200]
            : theme.palette.grey[800],
        borderTop: (theme) => `1px solid ${theme.palette.divider}`,
      }}
    >
      <Container maxWidth="lg">
        <Typography variant="body2" color="text.secondary" align="center">
          {'© '}
          {new Date().getFullYear()}{' '}
          <MuiLink color="inherit" component={RouterLink} to="/">
            BhashaBandu - Legal Application System
          </MuiLink>
          . All rights reserved.
        </Typography>
        <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
          <MuiLink component={RouterLink} to="/privacy-policy" color="inherit" sx={{ mx: 1 }}>
            Privacy Policy
          </MuiLink>
          |
          <MuiLink component={RouterLink} to="/terms-of-service" color="inherit" sx={{ mx: 1 }}>
            Terms of Service
          </MuiLink>
          |
          <MuiLink component={RouterLink} to="/contact-us" color="inherit" sx={{ mx: 1 }}>
            Contact Us
          </MuiLink>
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer;
