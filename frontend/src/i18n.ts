import { createI18n } from 'vue-i18n';
import en from './locales/en.json';
import bn from './locales/bn.json';

const messages = {
  en,
  bn,
};

export const i18n = createI18n({
  legacy: false, // Use Composition API
  locale: localStorage.getItem('locale') || 'en', // Default locale
  fallbackLocale: 'en',
  messages,
});
