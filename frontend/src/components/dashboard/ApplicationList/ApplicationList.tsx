// ============ src/components/dashboard/ApplicationList/ApplicationList.tsx ============
import React from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  Box,
  Typography,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import { Visibility, Edit, Download, Share } from "@mui/icons-material";
import { format } from "date-fns";

interface Application {
  id: number;
  application_id: string;
  title: string;
  status: string;
  created_at: string;
  submitted_at?: string;
  template: {
    name: string;
    form_type: string;
  };
}

interface ApplicationListProps {
  applications: Application[];
}

const ApplicationList: React.FC<ApplicationListProps> = ({ applications }) => {
  const navigate = useNavigate();

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
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

  const handleView = (applicationId: number) => {
    navigate(`/application/${applicationId}`);
  };

  const handleEdit = (applicationId: number) => {
    navigate(`/create-application?edit=${applicationId}`);
  };

  const handleDownload = (applicationId: number) => {
    window.open(`/api/documents/download/${applicationId}/`, "_blank");
  };

  const handleShare = (applicationId: number) => {
    // Implement sharing functionality
    navigator.clipboard.writeText(
      `${window.location.origin}/application/${applicationId}`
    );
  };

  if (applications.length === 0) {
    return (
      <Box textAlign="center" py={4}>
        <Typography variant="body1" color="textSecondary">
          No applications found. Create your first application to get started.
        </Typography>
      </Box>
    );
  }

  return (
    <TableContainer component={Paper} variant="outlined">
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Application ID</TableCell>
            <TableCell>Title</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Created</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {applications.map((application) => (
            <TableRow key={application.id} hover>
              <TableCell>
                <Typography variant="body2" fontWeight="bold">
                  {application.application_id}
                </Typography>
              </TableCell>
              <TableCell>
                <Typography variant="body2">{application.title}</Typography>
              </TableCell>
              <TableCell>
                <Chip
                  label={application.template.form_type}
                  size="small"
                  variant="outlined"
                />
              </TableCell>
              <TableCell>
                <Chip
                  label={application.status.replace("_", " ")}
                  size="small"
                  color={getStatusColor(application.status) as any}
                />
              </TableCell>
              <TableCell>
                <Typography variant="body2">
                  {format(new Date(application.created_at), "MMM dd, yyyy")}
                </Typography>
              </TableCell>
              <TableCell>
                <Box display="flex" gap={1}>
                  <Tooltip title="View Details">
                    <IconButton
                      size="small"
                      onClick={() => handleView(application.id)}
                    >
                      <Visibility />
                    </IconButton>
                  </Tooltip>
                  {application.status === "draft" && (
                    <Tooltip title="Edit">
                      <IconButton
                        size="small"
                        onClick={() => handleEdit(application.id)}
                      >
                        <Edit />
                      </IconButton>
                    </Tooltip>
                  )}
                  <Tooltip title="Download">
                    <IconButton
                      size="small"
                      onClick={() => handleDownload(application.id)}
                    >
                      <Download />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Share">
                    <IconButton
                      size="small"
                      onClick={() => handleShare(application.id)}
                    >
                      <Share />
                    </IconButton>
                  </Tooltip>
                </Box>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default ApplicationList;
