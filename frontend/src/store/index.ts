// ============ src/store/index.ts ============
import { configureStore } from "@reduxjs/toolkit";
import authReducer from "./slices/authSlice";
import formsReducer from "./slices/formsSlice";
import speechReducer from "./slices/speechSlice";
import uiReducer from "./slices/uiSlice";
import notificationReducer from "./slices/notificationSlice";

export const store = configureStore({
  reducer: {
    auth: authReducer,
    forms: formsReducer,
    speech: speechReducer,
    ui: uiReducer,
    notifications: notificationReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ["speech/setSpeechRecognition"],
        ignoredPaths: ["speech.recognition"],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
