// ============ src/utils/translations/index.ts ============
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import en from "./en";
import hi from "./hi";
import te from "./te";

const resources = {
  en: { translation: en },
  hi: { translation: hi },
  te: { translation: te },
};

i18n.use(initReactI18next).init({
  resources,
  lng: "en",
  fallbackLng: "en",
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
