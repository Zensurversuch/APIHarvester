import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  en: {
    translation: {
        appName: "APIHarvester",
        appDescription: "APIHarvester is a powerful tool designed to periodically fetch APIs and retrieve data efficiently. Automate your data collection, streamline your workflows, and focus on what matters most.",
        welcomeMessage: "Welcome to APIHarvester",
        login: "Login",
        loginTitle: "Login to APIHarvester",
        loginDescription: "Please enter your credentials to access your account.",
        loginEmail: "Email adress",
        loginPassword: "Password",
        loginPlaceholderEmail: "Enter email",
        loginPlaceholderPassword: "Enter password",
        learnMore: "Learn More",
        navHome: "Home",
        navLogin: "Login",
        navLogout: "Logout",
        apiListTitle: "API List",
        apiName: "API Name",
        apiDescription: "Description",
        apiEndpoint: "Endpoint",
        details: "Details",
        showDetails: "Show Details",
        hideDetails: "Hide Details",
        apiDetails: "API Details",
        apiDetailsDescription: "Details for API {{apiName}}"
    },
  },
};

i18n
  .use(initReactI18next) // Passes i18n down to react-i18next
  .init({
    resources, 
    lng: 'en', 
    fallbackLng: 'en', // Fallback language if translation not found
    interpolation: {
      escapeValue: false, 
    },
  });
export default i18n;
