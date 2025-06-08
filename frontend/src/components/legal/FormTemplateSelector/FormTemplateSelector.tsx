// ============ src/components/legal/FormTemplateSelector/FormTemplateSelector.tsx ============
import React, { useState } from "react";
import {
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Chip,
  Box,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from "@mui/material";
import { Search, Gavel, Description } from "@mui/icons-material";

// Use the same interface as in formsSlice
interface FormTemplate {
  id: number;
  name: string;
  form_type: string;
  description: string;
  language: string;
  court_types: string[];
  template_json: any;
  fields: any[];
}

interface FormTemplateSelectorProps {
  templates: FormTemplate[];
  onSelect: (template: FormTemplate) => void;
  loading: boolean;
}

const FormTemplateSelector: React.FC<FormTemplateSelectorProps> = ({
  templates,
  onSelect,
  loading,
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState("all");

  const filteredTemplates = templates.filter((template) => {
    const matchesSearch =
      template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      template.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType =
      filterType === "all" || template.form_type === filterType;
    return matchesSearch && matchesType;
  });

  const getFormTypeIcon = (type: string) => {
    switch (type) {
      case "petition":
        return <Gavel />;
      case "application":
        return <Description />;
      default:
        return <Description />;
    }
  };

  const getFormTypeColor = (type: string) => {
    switch (type) {
      case "petition":
        return "primary";
      case "application":
        return "secondary";
      case "complaint":
        return "error";
      default:
        return "default";
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <Typography>Loading templates...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box mb={3}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              placeholder="Search templates..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Filter by Type</InputLabel>
              <Select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                label="Filter by Type"
              >
                <MenuItem value="all">All Types</MenuItem>
                <MenuItem value="petition">Petition</MenuItem>
                <MenuItem value="application">Application</MenuItem>
                <MenuItem value="complaint">Complaint</MenuItem>
                <MenuItem value="appeal">Appeal</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Box>

      <Grid container spacing={3}>
        {filteredTemplates.map((template) => (
          <Grid item xs={12} md={6} lg={4} key={template.id}>
            <Card
              sx={{
                height: "100%",
                display: "flex",
                flexDirection: "column",
                transition: "transform 0.2s",
                "&:hover": {
                  transform: "translateY(-4px)",
                  boxShadow: 3,
                },
              }}
            >
              <CardContent sx={{ flexGrow: 1 }}>
                <Box display="flex" alignItems="center" mb={2}>
                  {getFormTypeIcon(template.form_type)}
                  <Typography variant="h6" ml={1}>
                    {template.name}
                  </Typography>
                </Box>

                <Typography variant="body2" color="textSecondary" paragraph>
                  {template.description}
                </Typography>

                <Box mb={2}>
                  <Chip
                    label={template.form_type}
                    color={getFormTypeColor(template.form_type) as any}
                    size="small"
                    sx={{ mr: 1 }}
                  />
                  <Chip
                    label={template.language.toUpperCase()}
                    variant="outlined"
                    size="small"
                  />
                </Box>

                {template.court_types && template.court_types.length > 0 && (
                  <Box>
                    <Typography variant="caption" color="textSecondary">
                      Applicable Courts:
                    </Typography>
                    <Typography variant="body2">
                      {template.court_types.join(", ")}
                    </Typography>
                  </Box>
                )}
              </CardContent>

              <CardActions>
                <Button
                  fullWidth
                  variant="contained"
                  onClick={() => onSelect(template)}
                >
                  Select Template
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {filteredTemplates.length === 0 && (
        <Box textAlign="center" py={4}>
          <Typography variant="h6" color="textSecondary">
            No templates found
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Try adjusting your search criteria
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default FormTemplateSelector;
