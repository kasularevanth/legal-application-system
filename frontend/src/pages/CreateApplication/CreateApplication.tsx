import React, { useState, useEffect } from "react";
import {
  Container,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
  Grid,
  Box,
  Button,
  Chip,
} from "@mui/material";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../../store";
import {
  fetchFormTemplates,
  createApplication,
  updateApplication,
} from "../../store/slices/formsSlice";
import FormTemplateSelector from "../../components/legal/FormTemplateSelector";
import LegalFormBuilder from "../../components/forms/LegalFormBuilder";
import { Gavel, Description, CheckCircle } from "@mui/icons-material";

const CreateApplication: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [searchParams] = useSearchParams();
  const editId = searchParams.get("edit");

  const { templates, loading, currentApplication } = useSelector(
    (state: RootState) => state.forms
  );

  const [activeStep, setActiveStep] = useState(0);
  const [selectedTemplate, setSelectedTemplate] = useState<any>(null);

  const steps = [
    { label: "Select Template", icon: <Description /> },
    { label: "Fill Application", icon: <Gavel /> },
    { label: "Review & Submit", icon: <CheckCircle /> },
  ];

  useEffect(() => {
    dispatch(fetchFormTemplates() as any);
  }, [dispatch]);

  useEffect(() => {
    if (editId && currentApplication) {
      setSelectedTemplate(currentApplication.template);
      setActiveStep(1);
    }
  }, [editId, currentApplication]);

  const handleTemplateSelect = (template: any) => {
    setSelectedTemplate(template);
    setActiveStep(1);
  };

  const handleFormSubmit = async (formData: any) => {
    try {
      if (editId) {
        await dispatch(
          updateApplication({
            id: parseInt(editId),
            data: { form_data: formData, status: "submitted" },
          }) as any
        );
      } else {
        await dispatch(
          createApplication({
            template_id: selectedTemplate.id,
            title: formData.title || `${selectedTemplate.name} Application`,
            form_data: formData,
          }) as any
        );
      }

      navigate("/dashboard");
    } catch (error) {
      console.error("Failed to submit application:", error);
    }
  };

  const handleFormSave = async (formData: any) => {
    try {
      if (editId) {
        await dispatch(
          updateApplication({
            id: parseInt(editId),
            data: { form_data: formData },
          }) as any
        );
      } else {
        await dispatch(
          createApplication({
            template_id: selectedTemplate.id,
            title: formData.title || `${selectedTemplate.name} Draft`,
            form_data: formData,
          }) as any
        );
      }
    } catch (error) {
      console.error("Failed to save application:", error);
    }
  };

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return (
          <FormTemplateSelector
            templates={templates}
            onSelect={handleTemplateSelect}
            loading={loading}
          />
        );
      case 1:
        return selectedTemplate ? (
          <LegalFormBuilder
            template={selectedTemplate}
            onSubmit={handleFormSubmit}
            onSave={handleFormSave}
            initialData={currentApplication?.form_data}
          />
        ) : null;
      default:
        return null;
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box mb={4}>
        <Typography variant="h4" gutterBottom>
          {editId ? "Edit Application" : "Create New Application"}
        </Typography>
        <Typography variant="body1" color="textSecondary">
          {editId
            ? "Update your existing application"
            : "Fill out a legal application using voice or text input"}
        </Typography>
      </Box>

      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Stepper activeStep={activeStep} alternativeLabel>
            {steps.map((step, index) => (
              <Step key={step.label}>
                <StepLabel icon={step.icon}>{step.label}</StepLabel>
              </Step>
            ))}
          </Stepper>
        </CardContent>
      </Card>

      {selectedTemplate && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box
              display="flex"
              alignItems="center"
              justifyContent="space-between"
            >
              <Box>
                <Typography variant="h6">{selectedTemplate.name}</Typography>
                <Typography variant="body2" color="textSecondary">
                  {selectedTemplate.description}
                </Typography>
              </Box>
              <Box>
                <Chip
                  label={selectedTemplate.form_type}
                  color="primary"
                  variant="outlined"
                />
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

      {renderStepContent()}
    </Container>
  );
};

export default CreateApplication;
