import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Keys and translations for visable Textes. To support potentially multiple languages and that the same texts are standardized
// Work in Progress: only some textes are alredy linked with key translations
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
        noAccount: "Don't have an account?",
        registerHere: "Register here",
        register: "Register",
        registerDescription: "Please fill in the details below to create a new account.",
        registerFirstName: "First Name",
        registerPlaceholderFirstName: "Enter First Name",
        registerLastName: "Last Name",
        registerPlaceholderLastName: "Enter Last Name",
        registerEmail: "Email",
        registerPlaceholderEmail: "Enter email",
        registerPassword: "Password",
        registerPlaceholderPassword: "Enter password",
        registerConfirmPassword: "Confirm Password",
        registerPlaceholderConfirmPassword: "Confirm your password",
        registerPasswordMismatch: "Passwords don´t match",
        registerPasswordHelpText: "Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one number, and one special character (e.g., !@#$%^&*).",
        registerError: "Registration failed. Please try again.",
        loginRedirectText: "Already have an account?",
        loginRedirectLink: "Login here",
        userCreatedSuccess: "User created successfully. You can now log in.",
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
        apiDetailsDescription: "Details for API {{apiName}}",
        subscriptionsTitle: "Subscriptions"

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
