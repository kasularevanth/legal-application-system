// ============ src/components/forms/LegalFormBuilder/LegalFormBuilder.tsx ============
import React, { useState, useEffect } from "react";
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  Button,
  Typography,
  Card,
  CardContent,
  LinearProgress,
} from "@mui/material";
import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../../../store";
import FormField from "../FormField";
import SpeechRecorder from "../../speech/SpeechRecorder";
import { analyzeSpeechForForm } from "../../../store/slices/speechSlice";

// Use the same interface as in formsSlice
interface FormTemplate {
  id: number;
  name: string;
  form_type: string;
  description: string;
  language: string;
  court_types: string[];
  template_json: any;
  fields: FormFieldConfig[];
}

interface FormFieldConfig {
  field_name: string;
  field_type: string;
  label: string;
  description: string;
  is_required: boolean;
  validation_rules: any;
  options: string[];
  order: number;
}

interface LegalFormBuilderProps {
  template: FormTemplate;
  onSubmit: (formData: any) => void;
  onSave: (formData: any) => void;
  initialData?: any;
}

const LegalFormBuilder: React.FC<LegalFormBuilderProps> = ({
  template,
  onSubmit,
  onSave,
  initialData,
}) => {
  const dispatch = useDispatch();
  const { transcription } = useSelector((state: RootState) => state.speech);

  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState<Record<string, any>>(
    initialData || {}
  );
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [showSpeechInput, setShowSpeechInput] = useState(false);

  const steps = [
    "Basic Information",
    "Legal Details",
    "Supporting Documents",
    "Review & Submit",
  ];
  const fieldsPerStep = Math.ceil(template.fields.length / steps.length);

  useEffect(() => {
    if (transcription) {
      dispatch(
        analyzeSpeechForForm({
          transcribed_text: transcription,
          template_id: template.id,
        }) as any
      );
    }
  }, [transcription, template.id, dispatch]);

  const getCurrentStepFields = () => {
    const startIndex = currentStep * fieldsPerStep;
    const endIndex = startIndex + fieldsPerStep;
    return template.fields
      .sort((a, b) => a.order - b.order)
      .slice(startIndex, endIndex);
  };

  const handleFieldChange = (fieldName: string, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [fieldName]: value,
    }));

    // Clear error if field is filled
    if (errors[fieldName] && value) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[fieldName];
        return newErrors;
      });
    }
  };

  const validateCurrentStep = () => {
    const currentFields = getCurrentStepFields();
    const newErrors: Record<string, string> = {};

    currentFields.forEach((field) => {
      if (field.is_required && !formData[field.field_name]) {
        newErrors[field.field_name] = `${field.label} is required`;
      }

      // Additional validation based on field type
      if (formData[field.field_name] && field.validation_rules) {
        // Add custom validation logic here
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateCurrentStep()) {
      if (currentStep < steps.length - 1) {
        setCurrentStep((prev) => prev + 1);
      } else {
        onSubmit(formData);
      }
    }
  };

  const handleBack = () => {
    setCurrentStep((prev) => prev - 1);
  };

  const handleSaveAsDraft = () => {
    onSave(formData);
  };

  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <Box>
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            {template.name}
          </Typography>
          <Typography variant="body2" color="textSecondary" paragraph>
            {template.description}
          </Typography>

          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{ mb: 3 }}
          />

          <Stepper activeStep={currentStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {showSpeechInput && (
            <Box mb={3}>
              <Typography variant="h6" gutterBottom>
                Voice Input
              </Typography>
              <SpeechRecorder
                onTranscriptionChange={(text: string) => {
                  // Auto-fill logic would be implemented here
                  console.log("Transcription:", text);
                }}
              />
            </Box>
          )}

          <Box>
            {getCurrentStepFields().map((field) => (
              <FormField
                key={field.field_name}
                config={field}
                value={formData[field.field_name] || ""}
                onChange={(value: any) =>
                  handleFieldChange(field.field_name, value)
                }
                error={errors[field.field_name]}
              />
            ))}
          </Box>

          <Box display="flex" justifyContent="space-between" mt={4}>
            <Box>
              <Button
                variant="outlined"
                onClick={() => setShowSpeechInput(!showSpeechInput)}
                sx={{ mr: 2 }}
              >
                {showSpeechInput ? "Hide" : "Use"} Voice Input
              </Button>
              <Button variant="outlined" onClick={handleSaveAsDraft}>
                Save as Draft
              </Button>
            </Box>

            <Box>
              <Button
                disabled={currentStep === 0}
                onClick={handleBack}
                sx={{ mr: 1 }}
              >
                Back
              </Button>
              <Button variant="contained" onClick={handleNext}>
                {currentStep === steps.length - 1 ? "Submit" : "Next"}
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default LegalFormBuilder;
