// ============ src/styles/globalStyles.ts ============
import { createGlobalStyle } from "styled-components";

export const GlobalStyles = createGlobalStyle`
  :root {
    --primary-color: #1976d2;
    --secondary-color: #dc004e;
    --background-color: #f5f5f5;
    --text-primary: #333333;
    --text-secondary: #666666;
    --border-color: #e0e0e0;
    --shadow-light: 0 2px 4px rgba(0,0,0,0.1);
    --shadow-medium: 0 4px 8px rgba(0,0,0,0.15);
    --shadow-heavy: 0 8px 16px rgba(0,0,0,0.2);
    --border-radius: 8px;
    --transition: all 0.3s ease;
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: 'Roboto', 'Helvetica', 'Arial', sans-serif;
    line-height: 1.6;
    color: var(--text-primary);
    background-color: var(--background-color);
  }

  .speech-recording {
    animation: pulse 1.5s infinite;
  }

  @keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.6; }
    100% { opacity: 1; }
  }

  .form-step-active {
    border-left: 4px solid var(--primary-color);
    background-color: rgba(25, 118, 210, 0.05);
  }

  .loading-spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid rgba(25, 118, 210, 0.3);
    border-radius: 50%;
    border-top-color: var(--primary-color);
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;
