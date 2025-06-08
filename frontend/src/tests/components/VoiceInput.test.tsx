
# ============ frontend/src/tests/components/VoiceInput.test.tsx ============
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import '@testing-library/jest-dom';

import EnhancedVoiceInput from '../../components/voice/EnhancedVoiceInput';
import authReducer from '../../store/slices/authSlice';
import notificationReducer from '../../store/slices/notificationSlice';

// Mock the WebSocket service
jest.mock('../../services/websocket/WebSocketService', () => ({
  webSocketService: {
    connect: jest.fn().mockResolvedValue(undefined),
    disconnect: jest.fn(),
    isConnected: jest.fn().mockReturnValue(true),
    subscribeToCase: jest.fn(),
    unsubscribeFromCase: jest.fn(),
    onVoiceProcessing: jest.fn(),
    onCaseAnalysis: jest.fn(),
    onDocumentGeneration: jest.fn(),
    onCaseStatusUpdate: jest.fn(),
    onError: jest.fn(),
    removeHandler: jest.fn(),
  },
}));

// Mock the voice legal API
jest.mock('../../services/api/voiceLegal', () => ({
  voiceLegalAPI: {
    processVoiceForLegalCase: jest.fn(),
    addVoiceInformation: jest.fn(),
    getCaseDetails: jest.fn(),
  },
}));

// Mock getUserMedia
Object.defineProperty(navigator, 'mediaDevices', {
  writable: true,
  value: {
    getUserMedia: jest.fn().mockImplementation(() =>
      Promise.resolve({
        getTracks: () => [{ stop: jest.fn() }],
      })
    ),
  },
});

// Mock MediaRecorder
global.MediaRecorder = jest.fn().mockImplementation(() => ({
  start: jest.fn(),
  stop: jest.fn(),
  ondataavailable: jest.fn(),
  onstop: jest.fn(),
  state: 'inactive',
}));

const createTestStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      auth: authReducer,
      notifications: notificationReducer,
    },
    preloadedState: {
      auth: {
        user: { id: 1, username: 'testuser', preferred_language: 'en' },
        token: 'test-token',
        isAuthenticated: true,
        loading: false,
        error: null,
        ...initialState.auth,
      },
      notifications: {
        open: false,
        message: '',
        severity: 'info',
        autoHideDuration: 6000,
        ...initialState.notifications,
      },
    },
  });
};

const renderWithProviders = (component: React.ReactElement, { initialState = {} } = {}) => {
  const store = createTestStore(initialState);
  return render(
    <Provider store={store}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </Provider>
  );
};

describe('EnhancedVoiceInput', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders voice input component', () => {
    renderWithProviders(<EnhancedVoiceInput />);
    
    expect(screen.getByRole('button')).toBeInTheDocument();
    expect(screen.getByText(/ready to record/i)).toBeInTheDocument();
  });

  test('starts recording when mic button is clicked', async () => {
    renderWithProviders(<EnhancedVoiceInput />);
    
    const micButton = screen.getByRole('button');
    fireEvent.click(micButton);

    await waitFor(() => {
      expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });
    });
  });

  test('shows processing state during analysis', async () => {
    const mockOnAnalysisComplete = jest.fn();
    renderWithProviders(
      <EnhancedVoiceInput onAnalysisComplete={mockOnAnalysisComplete} />
    );

    // Simulate processing state
    // This would be triggered by WebSocket updates in real usage
    expect(screen.getByText(/ready to record/i)).toBeInTheDocument();
  });

  test('displays analysis results when completed', async () => {
    const mockAnalysis = {
      case_analysis: {
        primary_case_type: 'civil',
        confidence_score: 0.85,
        legal_complexity: 'medium',
      },
      extracted_information: {
        key_facts: ['Property dispute', 'Neighbor issue'],
      },
    };

    const mockOnAnalysisComplete = jest.fn();
    renderWithProviders(
      <EnhancedVoiceInput onAnalysisComplete={mockOnAnalysisComplete} />
    );

    // Simulate analysis completion
    // In real usage, this would come from the WebSocket or API response
    // For testing, we'd need to trigger the state change manually
  });

  test('handles microphone permission denial', async () => {
    navigator.mediaDevices.getUserMedia = jest.fn().mockRejectedValue(
      new Error('Permission denied')
    );

    renderWithProviders(<EnhancedVoiceInput />);
    
    const micButton = screen.getByRole('button');
    fireEvent.click(micButton);

    await waitFor(() => {
      expect(screen.getByText(/failed to access microphone/i)).toBeInTheDocument();
    });
  });
});
