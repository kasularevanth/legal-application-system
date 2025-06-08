

// ============ frontend/src/components/common/NotificationHandler/NotificationHandler.tsx (New) ============
import React from 'react';
import { Snackbar, Alert } from '@mui/material';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../../store';
import { hideNotification } from '../../../store/slices/notificationSlice';

const NotificationHandler: React.FC = () => {
  const dispatch = useDispatch();
  const { open, message, severity, autoHideDuration } = useSelector(
    (state: RootState) => state.notifications
  );

  const handleClose = () => {
    dispatch(hideNotification());
  };

  return (
    <Snackbar
      open={open}
      autoHideDuration={autoHideDuration}
      onClose={handleClose}
      anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
    >
      <Alert
        onClose={handleClose}
        severity={severity}
        variant="filled"
        sx={{ width: '100%' }}
      >
        {message}
      </Alert>
    </Snackbar>
  );
};

export default NotificationHandler;
