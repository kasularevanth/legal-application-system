// ============ frontend/src/App.tsx (Updated) ============
import React, { useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { GlobalStyles } from "./styles/globalStyles";
import { RootState } from "./store";
import { checkAuth } from "./store/slices/authSlice";
import { useWebSocket } from "./hooks/useWebSocket";
import { theme } from "./styles/theme";

// Layout Components
import Layout from "./components/common/Layout";
import ProtectedRoute from "./components/auth/ProtectedRoute";
import NotificationHandler from "./components/common/NotificationHandler";

// Page Components
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import CreateApplication from "./pages/CreateApplication";
import ApplicationDetails from "./pages/ApplicationDetails";
import KnowledgeBase from "./pages/KnowledgeBase";
import VoiceLegalAssistant from "./pages/VoiceLegalAssistant";
import DocumentGeneration from "./pages/DocumentGeneration";
import CaseDetails from "./pages/CaseDetails";
import VoiceInputPage from "./pages/VoiceInputPage";

// Error Boundary Component
import ErrorBoundary from "./components/common/ErrorBoundary";

const App: React.FC = () => {
  const dispatch = useDispatch();
  const { isAuthenticated, loading } = useSelector(
    (state: RootState) => state.auth
  );

  // Initialize WebSocket connection
  useWebSocket();

  useEffect(() => {
    dispatch(checkAuth() as any);
  }, [dispatch]);

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        Loading...
      </div>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <GlobalStyles />
      <ErrorBoundary>
        <NotificationHandler />
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Home />} />
            
            {/* Authentication Routes */}
            <Route
              path="/login"
              element={isAuthenticated ? <Navigate to="/dashboard" /> : <Login />}
            />
            <Route
              path="/register"
              element={
                isAuthenticated ? <Navigate to="/dashboard" /> : <Register />
              }
            />

            {/* Protected Routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            
            {/* Voice Legal Assistant Routes */}
            <Route
              path="/voice-assistant"
              element={
                <ProtectedRoute>
                  <VoiceLegalAssistant />
                </ProtectedRoute>
              }
            />
            <Route
              path="/voice-input"
              element={
                <ProtectedRoute>
                  <VoiceInputPage />
                </ProtectedRoute>
              }
            />

            {/* Traditional Form Routes */}
            <Route
              path="/create-application"
              element={
                <ProtectedRoute>
                  <CreateApplication />
                </ProtectedRoute>
              }
            />
            <Route
              path="/application/:id"
              element={
                <ProtectedRoute>
                  <ApplicationDetails />
                </ProtectedRoute>
              }
            />

            {/* Legal Case Routes */}
            <Route
              path="/cases/:id"
              element={
                <ProtectedRoute>
                  <CaseDetails />
                </ProtectedRoute>
              }
            />

            {/* Document Generation Routes */}
            <Route
              path="/generate-documents/:caseId"
              element={
                <ProtectedRoute>
                  <DocumentGeneration />
                </ProtectedRoute>
              }
            />

            {/* Public Routes */}
            <Route path="/knowledge-base" element={<KnowledgeBase />} />
            
            {/* Catch-all route */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </ErrorBoundary>
    </ThemeProvider>
  );
};

export default App;