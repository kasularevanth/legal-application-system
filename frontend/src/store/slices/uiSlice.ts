import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UIState {
  isLoading: boolean;
  // Potentially other UI states like theme, sidebarOpen, etc.
}

const initialState: UIState = {
  isLoading: false,
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    // Potentially other reducers for UI state changes
  },
});

export const { setLoading } = uiSlice.actions;
export default uiSlice.reducer;
