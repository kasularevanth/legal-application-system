// ============ src/components/dashboard/StatusTracker/StatusTracker.tsx ============
import React from "react";
import {
  Box,
  Typography,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from "@mui/material";
import { Circle, CheckCircle, Error, AccessTime } from "@mui/icons-material";

interface Application {
  id: number;
  title: string;
  status: string;
  created_at: string;
}

interface StatusTrackerProps {
  applications: Application[];
}

const StatusTracker: React.FC<StatusTrackerProps> = ({ applications }) => {
  const statusSteps = [
    { key: "draft", label: "Draft Created", icon: <Circle /> },
    { key: "submitted", label: "Submitted", icon: <AccessTime /> },
    { key: "under_review", label: "Under Review", icon: <AccessTime /> },
    { key: "approved", label: "Approved", icon: <CheckCircle /> },
    { key: "completed", label: "Completed", icon: <CheckCircle /> },
  ];

  const getActiveStep = (status: string) => {
    const stepIndex = statusSteps.findIndex((step) => step.key === status);
    return stepIndex >= 0 ? stepIndex : 0;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
      case "approved":
        return <CheckCircle color="success" />;
      case "rejected":
        return <Error color="error" />;
      case "under_review":
      case "submitted":
        return <AccessTime color="warning" />;
      default:
        return <Circle color="disabled" />;
    }
  };

  const recentApplications = applications
    .filter((app) => app.status !== "draft")
    .slice(0, 3);

  return (
    <Box>
      {recentApplications.length > 0 ? (
        <List>
          {recentApplications.map((application, index) => (
            <React.Fragment key={application.id}>
              <ListItem>
                <ListItemIcon>{getStatusIcon(application.status)}</ListItemIcon>
                <ListItemText
                  primary={application.title}
                  secondary={`Status: ${application.status.replace("_", " ")}`}
                />
              </ListItem>
              {index < recentApplications.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>
      ) : (
        <Box textAlign="center" py={2}>
          <Typography variant="body2" color="textSecondary">
            No active applications to track
          </Typography>
        </Box>
      )}

      {recentApplications.length > 0 && (
        <Box mt={3}>
          <Typography variant="subtitle2" gutterBottom>
            Typical Application Process
          </Typography>
          <Stepper activeStep={-1} orientation="vertical" sx={{ pl: 2 }}>
            {statusSteps.map((step, index) => (
              <Step key={step.key}>
                <StepLabel>{step.label}</StepLabel>
              </Step>
            ))}
          </Stepper>
        </Box>
      )}
    </Box>
  );
};

export default StatusTracker;
