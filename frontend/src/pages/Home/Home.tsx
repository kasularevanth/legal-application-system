// ============ src/pages/Home/Home.tsx ============
import React from "react";
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  CardContent,
  Chip,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import { useSelector } from "react-redux";
import { RootState } from "../../store";
import {
  VoiceChat,
  TranslateSharp,
  Description,
  TrackChanges,
} from "@mui/icons-material";
import { StyledHeroSection, StyledFeatureCard } from "./Home.styles";

const Home: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);

  const features = [
    {
      icon: <VoiceChat color="primary" fontSize="large" />,
      title: "Voice-Powered Forms",
      description: "Fill legal forms using your voice in regional languages",
    },
    {
      icon: <TranslateSharp color="primary" fontSize="large" />,
      title: "Multi-Language Support",
      description: "Support for 12+ Indian regional languages",
    },
    {
      icon: <Description color="primary" fontSize="large" />,
      title: "Legal Templates",
      description: "Pre-built templates for common legal applications",
    },
    {
      icon: <TrackChanges color="primary" fontSize="large" />,
      title: "Application Tracking",
      description: "Track your application status in real-time",
    },
  ];

  const handleGetStarted = () => {
    if (isAuthenticated) {
      navigate("/dashboard");
    } else {
      navigate("/register");
    }
  };

  return (
    <Box>
      <StyledHeroSection>
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center" minHeight="80vh">
            <Grid item xs={12} md={6}>
              <Typography variant="h2" component="h1" gutterBottom>
                Simplify Legal Forms with{" "}
                <span style={{ color: "#1976d2" }}>Voice Technology</span>
              </Typography>
              <Typography variant="h5" paragraph color="textSecondary">
                File legal applications easily using regional speech
                recognition. No more complex paperwork - just speak and we'll
                handle the rest.
              </Typography>
              <Box mt={4}>
                <Button
                  variant="contained"
                  size="large"
                  onClick={handleGetStarted}
                  sx={{ mr: 2 }}
                >
                  Get Started
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={() => navigate("/knowledge-base")}
                >
                  Learn More
                </Button>
              </Box>
              <Box mt={3}>
                <Chip label="BHASHINI Powered" sx={{ mr: 1 }} />
                <Chip label="AI-Assisted" sx={{ mr: 1 }} />
                <Chip label="Secure" />
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box
                component="img"
                src="https://png.pngtree.com/png-vector/20210731/ourmid/pngtree-legal-court-trial-character-illustration-png-image_3755439.jpg"
                alt="Legal Forms Illustration"
                sx={{
                  maxWidth: 500,
                  height: "auto",
                }}
              />
            </Grid>
          </Grid>
        </Container>
      </StyledHeroSection>

      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography variant="h3" align="center" gutterBottom>
          Why Choose Our Platform?
        </Typography>
        <Typography variant="h6" align="center" paragraph color="textSecondary">
          Democratizing access to legal services through technology
        </Typography>

        <Grid container spacing={4} mt={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <StyledFeatureCard>
                <CardContent sx={{ textAlign: "center" }}>
                  <Box mb={2}>{feature.icon}</Box>
                  <Typography variant="h6" gutterBottom>
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </StyledFeatureCard>
            </Grid>
          ))}
        </Grid>

        <Box mt={8} textAlign="center">
          <Typography variant="h4" gutterBottom>
            Supported Languages
          </Typography>
          <Box mt={3}>
            {[
              "English",
              "हिंदी",
              "తెలుగు",
              "தமிழ்",
              "বাংলা",
              "ગુજરાતી",
              "ಕನ್ನಡ",
              "മലയാളം",
              "मराठी",
              "ଓଡ଼ିଆ",
              "ਪੰਜਾਬੀ",
              "اردو",
            ].map((lang) => (
              <Chip
                key={lang}
                label={lang}
                sx={{ m: 0.5 }}
                variant="outlined"
              />
            ))}
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default Home;
