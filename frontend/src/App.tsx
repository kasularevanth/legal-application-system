// ============ src/App.tsx ============
import React, { useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { GlobalStyles } from "./styles/globalStyles";
import { RootState } from "./store";
import { checkAuth } from "./store/slices/authSlice";
import Layout from "./components/common/Layout";
import ProtectedRoute from "./components/auth/ProtectedRoute";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import CreateApplication from "./pages/CreateApplication";
import ApplicationDetails from "./pages/ApplicationDetails";
import KnowledgeBase from "./pages/KnowledgeBase";

const App: React.FC = () => {
  const dispatch = useDispatch();
  const { isAuthenticated, loading } = useSelector(
    (state: RootState) => state.auth
  );

  useEffect(() => {
    dispatch(checkAuth() as any);
  }, [dispatch]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <>
      <GlobalStyles />
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
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
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
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
          <Route path="/knowledge-base" element={<KnowledgeBase />} />
        </Route>
      </Routes>
    </>
  );
};

export default App;
