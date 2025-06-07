# ============ frontend/src/components/__tests__/SpeechRecorder.test.tsx ============
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import SpeechRecorder from '../speech/SpeechRecorder/SpeechRecorder';
import speechReducer from '../../store/slices/speechSlice';

const createTestStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      speech: speechReducer,
    },
    preloadedState: {
      speech: {
        isRecording: false,
        isProcessing: false,
        transcription: '',
        confidence: 0,
        language: 'hi',
        recognition: null,
        error: null,
        ...initialState,
      },
    },
  });
};

describe('SpeechRecorder', () => {
  it('renders recording button', () => {
    const store = createTestStore();
    render(
      <Provider store={store}>
        <SpeechRecorder />
      </Provider>
    );
    
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('shows recording state when active', () => {
    const store = createTestStore({ isRecording: true });
    render(
      <Provider store={store}>
        <SpeechRecorder />
      </Provider>
    );
    
    expect(screen.getByText(/recording/i)).toBeInTheDocument();
  });

  it('displays transcription when available', () => {
    const store = createTestStore({ 
      transcription: 'Test transcription text' 
    });
    render(
      <Provider store={store}>
        <SpeechRecorder />
      </Provider>
    );
    
    expect(screen.getByText('Test transcription text')).toBeInTheDocument();
  });
});