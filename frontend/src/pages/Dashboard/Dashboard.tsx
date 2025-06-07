// ============ src/pages/Dashboard/Dashboard.tsx ============
import React, { useEffect } from "react";
import {
  Container,
  Grid,
  Typography,
  Card,
  CardContent,
  Button,
  Box,
  Chip,
  LinearProgress,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { RootState } from "../../store";
import { fetchUserApplications } from "../../store/slices/formsSlice";
import {
  Add,
  Description,
  AccessTime,
  CheckCircle,
  Error,
} from "@mui/icons-material";
import ApplicationList from "../../components/dashboard/ApplicationList";
import StatusTracker from "../../components/dashboard/StatusTracker";

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { user } = useSelector((state: RootState) => state.auth);
  const { applications, loading } = useSelector(
    (state: RootState) => state.forms
  );

  useEffect(() => {
    dispatch(fetchUserApplications() as any);
  }, [dispatch]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "success";
      case "approved":
        return "success";
      case "under_review":
        return "warning";
      case "rejected":
        return "error";
      case "submitted":
        return "info";
      default:
        return "default";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
      case "approved":
        return <CheckCircle />;
      case "under_review":
        return <AccessTime />;
      case "rejected":
        return <Error />;
      default:
        return <Description />;
    }
  };

  const stats = {
    total: applications.length,
    pending: applications.filter((app) =>
      ["draft", "submitted", "under_review"].includes(app.status)
    ).length,
    completed: applications.filter((app) =>
      ["approved", "completed"].includes(app.status)
    ).length,
    rejected: applications.filter((app) => app.status === "rejected").length,
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={4}
      >
        <Box>
          <Typography variant="h4" gutterBottom>
            Welcome back, {user?.first_name || user?.username}!
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Manage your legal applications and track their progress
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => navigate("/create-application")}
          size="large"
        >
          New Application
        </Button>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box
                display="flex"
                alignItems="center"
                justifyContent="space-between"
              >
                <Box>
                  <Typography variant="h6" color="textSecondary" gutterBottom>
                    Total Applications
                  </Typography>
                  <Typography variant="h3">{stats.total}</Typography>
                </Box>
                <Description color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box
                display="flex"
                alignItems="center"
                justifyContent="space-between"
              >
                <Box>
                  <Typography variant="h6" color="textSecondary" gutterBottom>
                    Pending
                  </Typography>
                  <Typography variant="h3">{stats.pending}</Typography>
                </Box>
                <AccessTime color="warning" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box
                display="flex"
                alignItems="center"
                justifyContent="space-between"
              >
                <Box>
                  <Typography variant="h6" color="textSecondary" gutterBottom>
                    Completed
                  </Typography>
                  <Typography variant="h3">{stats.completed}</Typography>
                </Box>
                <CheckCircle color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box
                display="flex"
                alignItems="center"
                justifyContent="space-between"
              >
                <Box>
                  <Typography variant="h6" color="textSecondary" gutterBottom>
                    Rejected
                  </Typography>
                  <Typography variant="h3">{stats.rejected}</Typography>
                </Box>
                <Error color="error" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Applications
              </Typography>
              {loading ? (
                <LinearProgress />
              ) : (
                <ApplicationList applications={applications.slice(0, 5)} />
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box display="flex" flexDirection="column" gap={2}>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => navigate("/create-application")}
                >
                  Create New Application
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => navigate("/knowledge-base")}
                >
                  Legal Knowledge Base
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() =>
                    window.open("/api/documents/download-all/", "_blank")
                  }
                >
                  Download All Documents
                </Button>
              </Box>
            </CardContent>
          </Card>

          <Box mt={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Application Status Overview
                </Typography>
                <StatusTracker applications={applications} />
              </CardContent>
            </Card>
          </Box>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
