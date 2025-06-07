import React from 'react';
import { Container, Typography, Paper, Box, Avatar, Grid, TextField, Button } from '@mui/material';
import { deepOrange } from '@mui/material/colors'; // Example color

// Placeholder for UserProfile content
const UserProfile: React.FC = () => {
  // Mock user data - replace with actual data fetching
  const user = {
    name: 'John Doe',
    email: 'john.doe@example.com',
    initials: 'JD',
    bio: 'Legal professional with 5 years of experience in corporate law.',
    phone: '123-456-7890',
    address: '123 Legal St, Lawsville, CA 90210'
  };

  const [isEditing, setIsEditing] = React.useState(false);
  // Add state for form fields if implementing editing

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Avatar sx={{ bgcolor: deepOrange[500], width: 80, height: 80, mr: 2, fontSize: '2rem' }}>
            {user.initials}
          </Avatar>
          <Typography variant="h4" gutterBottom component="div">
            {user.name}
          </Typography>
        </Box>

        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <TextField
              label="Email Address"
              fullWidth
              value={user.email}
              InputProps={{ readOnly: !isEditing }}
              variant={isEditing ? "outlined" : "standard"}
              sx={{ mb: 2 }}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              label="Phone Number"
              fullWidth
              value={user.phone}
              InputProps={{ readOnly: !isEditing }}
              variant={isEditing ? "outlined" : "standard"}
              sx={{ mb: 2 }}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              label="Address"
              fullWidth
              value={user.address}
              InputProps={{ readOnly: !isEditing }}
              variant={isEditing ? "outlined" : "standard"}
              sx={{ mb: 2 }}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              label="Biography"
              fullWidth
              multiline
              rows={4}
              value={user.bio}
              InputProps={{ readOnly: !isEditing }}
              variant={isEditing ? "outlined" : "standard"}
              sx={{ mb: 2 }}
            />
          </Grid>
        </Grid>
        
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
          {isEditing ? (
            <>
              <Button variant="outlined" onClick={() => setIsEditing(false)} sx={{ mr: 1 }}>
                Cancel
              </Button>
              <Button variant="contained" onClick={() => { /* Handle save */ setIsEditing(false); }}>
                Save Changes
              </Button>
            </>
          ) : (
            <Button variant="contained" onClick={() => setIsEditing(true)}>
              Edit Profile
            </Button>
          )}
        </Box>
      </Paper>
    </Container>
  );
};

export default UserProfile;
