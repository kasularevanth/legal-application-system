import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import LoginForm from '../../components/auth/LoginForm'; // Assuming LoginForm will be created/fixed later

const Login: React.FC = () => {
  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Typography component="h1" variant="h5">
          Sign in
        </Typography>
        <LoginForm />
      </Box>
    </Container>
  );
};

export default Login;
