// ============ src/components/forms/FormField/FormField.tsx ============
import React from "react";
import {
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  FormHelperText,
  Checkbox,
  FormControlLabel,
  Box,
  Typography,
  IconButton,
  Tooltip,
} from "@mui/material";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { Help } from "@mui/icons-material";
import SpeechRecorder from "../../speech/SpeechRecorder";

interface FormFieldProps {
  config: {
    field_name: string;
    field_type: string;
    label: string;
    description: string;
    is_required: boolean;
    validation_rules: any;
    options: string[];
  };
  value: any;
  onChange: (value: any) => void;
  error?: string;
  enableSpeech?: boolean;
}

const FormField: React.FC<FormFieldProps> = ({
  config,
  value,
  onChange,
  error,
  enableSpeech = false,
}) => {
  const { field_type, label, description, is_required, options } = config;

  const renderField = () => {
    switch (field_type) {
      case "text":
      case "email":
      case "phone":
        return (
          <TextField
            fullWidth
            label={label}
            type={
              field_type === "email"
                ? "email"
                : field_type === "phone"
                ? "tel"
                : "text"
            }
            value={value}
            onChange={(e) => onChange(e.target.value)}
            required={is_required}
            error={!!error}
            helperText={error || description}
            variant="outlined"
          />
        );

      case "textarea":
        return (
          <TextField
            fullWidth
            label={label}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            required={is_required}
            error={!!error}
            helperText={error || description}
            variant="outlined"
            multiline
            rows={4}
          />
        );

      case "number":
        return (
          <TextField
            fullWidth
            label={label}
            type="number"
            value={value}
            onChange={(e) => onChange(Number(e.target.value))}
            required={is_required}
            error={!!error}
            helperText={error || description}
            variant="outlined"
          />
        );

      case "select":
        return (
          <FormControl fullWidth error={!!error}>
            <InputLabel>{label}</InputLabel>
            <Select
              value={value}
              onChange={(e) => onChange(e.target.value)}
              label={label}
              required={is_required}
            >
              {options.map((option) => (
                <MenuItem key={option} value={option}>
                  {option}
                </MenuItem>
              ))}
            </Select>
            <FormHelperText>{error || description}</FormHelperText>
          </FormControl>
        );

      case "checkbox":
        return (
          <FormControlLabel
            control={
              <Checkbox
                checked={value || false}
                onChange={(e) => onChange(e.target.checked)}
              />
            }
            label={label}
          />
        );

      case "date":
        return (
          <DatePicker
            label={label}
            value={value}
            onChange={(newValue) => onChange(newValue)}
            renderInput={(params) => (
              <TextField
                {...params}
                fullWidth
                required={is_required}
                error={!!error}
                helperText={error || description}
              />
            )}
          />
        );

      default:
        return (
          <TextField
            fullWidth
            label={label}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            required={is_required}
            error={!!error}
            helperText={error || description}
            variant="outlined"
          />
        );
    }
  };

  return (
    <Box mb={3}>
      <Box display="flex" alignItems="center" mb={1}>
        <Typography variant="subtitle1" component="label">
          {label}
          {is_required && <span style={{ color: "red" }}> *</span>}
        </Typography>
        {description && (
          <Tooltip title={description}>
            <IconButton size="small">
              <Help fontSize="small" />
            </IconButton>
          </Tooltip>
        )}
      </Box>

      {renderField()}

      {enableSpeech && ["text", "textarea"].includes(field_type) && (
        <Box mt={2}>
          <SpeechRecorder
            onTranscriptionChange={(text) => {
              if (field_type === "textarea") {
                onChange(value ? `${value} ${text}` : text);
              } else {
                onChange(text);
              }
            }}
          />
        </Box>
      )}
    </Box>
  );
};

export default FormField;
