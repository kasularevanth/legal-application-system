import { createSlice, PayloadAction } from '@reduxjs/toolkit';

type NotificationSeverity = 'success' | 'error' | 'warning' | 'info';

interface NotificationState {
  open: boolean;
  message: string;
  severity: NotificationSeverity;
  autoHideDuration: number | null;
}

const initialState: NotificationState = {
  open: false,
  message: '',
  severity: 'info',
  autoHideDuration: 6000,
};

const notificationSlice = createSlice({
  name: 'notification',
  initialState,
  reducers: {
    showNotification: (state, action: PayloadAction<{ message: string; severity?: NotificationSeverity; autoHideDuration?: number | null }>) => {
      state.open = true;
      state.message = action.payload.message;
      state.severity = action.payload.severity || 'info';
      state.autoHideDuration = action.payload.autoHideDuration === undefined ? 6000 : action.payload.autoHideDuration;
    },
    hideNotification: (state) => {
      state.open = false;
    },
  },
});

export const { showNotification, hideNotification } = notificationSlice.actions;
export default notificationSlice.reducer;
