// ============ src/pages/Home/Home.styles.ts ============
import styled from "styled-components";
import { Box, Card } from "@mui/material";

export const StyledHeroSection = styled(Box)`
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 80vh;
  display: flex;
  align-items: center;
`;

export const StyledFeatureCard = styled(Card)`
  height: 100%;
  transition: transform 0.3s ease-in-out;

  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  }
`;
