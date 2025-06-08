// ============ src/components/common/Layout/Layout.tsx ============
import React, { ReactNode } from "react";
import { Box, Container } from "@mui/material";
import { Outlet } from "react-router-dom";

interface LayoutProps {
  children?: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      {/* Placeholder for Header */}
      <Container component="main" sx={{ flexGrow: 1, py: 3 }}>
        {children || <Outlet />}
      </Container>
      {/* Placeholder for Footer */}
    </Box>
  );
};

export default Layout;
