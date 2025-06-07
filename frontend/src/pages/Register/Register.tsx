import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import RegisterForm from '../../components/auth/RegisterForm'; // Assuming RegisterForm will be created/fixed later

const Register: React.FC = () => {
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
          Sign up
        </Typography>
        <RegisterForm />
      </Box>
    </Container>
  );
};

export default Register;
