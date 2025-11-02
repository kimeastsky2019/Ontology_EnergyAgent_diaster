/**
 * i18n Configuration for Energy Analysis Platform
 * Supports Korean, English, Japanese, and Chinese
 */

// Translation resources
const translations = {
  ko: require('./locales/ko.json'),
  en: require('./locales/en.json'),
  ja: require('./locales/ja.json'),
  zh: require('./locales/zh.json')
};

// Available languages configuration
const availableLanguages = {
  ko: { name: '한국어', flag: '🇰🇷', code: 'ko' },
  en: { name: 'English', flag: '🇺🇸', code: 'en' },
  ja: { name: '日本語', flag: '🇯🇵', code: 'ja' },
  zh: { name: '中文', flag: '🇨🇳', code: 'zh' }
};

// Default language
const defaultLanguage = 'ko';

/**
 * Get translation for a given key and language
 * @param {string} key - Translation key (e.g., 'navigation.home')
 * @param {string} lang - Language code
 * @param {object} variables - Variables to interpolate
 * @returns {string} Translated text
 */
function getTranslation(key, lang = defaultLanguage, variables = {}) {
  const langData = translations[lang] || translations[defaultLanguage];
  
  // Navigate through nested object using dot notation
  const keys = key.split('.');
  let value = langData;
  
  for (const k of keys) {
    if (value && typeof value === 'object' && k in value) {
      value = value[k];
    } else {
      // Fallback to default language if key not found
      const defaultData = translations[defaultLanguage];
      let fallbackValue = defaultData;
      for (const fallbackKey of keys) {
        if (fallbackValue && typeof fallbackValue === 'object' && fallbackKey in fallbackValue) {
          fallbackValue = fallbackValue[fallbackKey];
        } else {
          return key; // Return key if not found in any language
        }
      }
      value = fallbackValue;
      break;
    }
  }
  
  // Handle string interpolation
  if (typeof value === 'string' && Object.keys(variables).length > 0) {
    return value.replace(/\{\{(\w+)\}\}/g, (match, varName) => {
      return variables[varName] || match;
    });
  }
  
  return value || key;
}

/**
 * Get all available languages
 * @returns {object} Available languages object
 */
function getAvailableLanguages() {
  return availableLanguages;
}

/**
 * Check if language is supported
 * @param {string} lang - Language code
 * @returns {boolean} True if language is supported
 */
function isLanguageSupported(lang) {
  return lang in availableLanguages;
}

/**
 * Get language name with flag
 * @param {string} lang - Language code
 * @returns {string} Language name with flag
 */
function getLanguageDisplayName(lang) {
  const langInfo = availableLanguages[lang];
  return langInfo ? `${langInfo.flag} ${langInfo.name}` : lang;
}

/**
 * Get browser language preference
 * @returns {string} Browser language code
 */
function getBrowserLanguage() {
  const browserLang = navigator.language || navigator.userLanguage;
  const langCode = browserLang.split('-')[0]; // Extract language code (e.g., 'en' from 'en-US')
  
  return isLanguageSupported(langCode) ? langCode : defaultLanguage;
}

/**
 * Get language from URL parameter
 * @returns {string} Language code from URL
 */
function getLanguageFromURL() {
  const urlParams = new URLSearchParams(window.location.search);
  const langParam = urlParams.get('lang');
  
  return isLanguageSupported(langParam) ? langParam : null;
}

/**
 * Set language in URL parameter
 * @param {string} lang - Language code
 */
function setLanguageInURL(lang) {
  if (!isLanguageSupported(lang)) return;
  
  const url = new URL(window.location);
  url.searchParams.set('lang', lang);
  window.history.pushState({}, '', url);
}

/**
 * Get language from localStorage
 * @returns {string} Language code from localStorage
 */
function getLanguageFromStorage() {
  const storedLang = localStorage.getItem('language');
  return isLanguageSupported(storedLang) ? storedLang : null;
}

/**
 * Set language in localStorage
 * @param {string} lang - Language code
 */
function setLanguageInStorage(lang) {
  if (!isLanguageSupported(lang)) return;
  localStorage.setItem('language', lang);
}

/**
 * Get current language with fallback priority:
 * 1. URL parameter
 * 2. localStorage
 * 3. Browser language
 * 4. Default language
 * @returns {string} Current language code
 */
function getCurrentLanguage() {
  return getLanguageFromURL() || 
         getLanguageFromStorage() || 
         getBrowserLanguage() || 
         defaultLanguage;
}

/**
 * Change language and update storage/URL
 * @param {string} lang - Language code
 */
function changeLanguage(lang) {
  if (!isLanguageSupported(lang)) return;
  
  setLanguageInStorage(lang);
  setLanguageInURL(lang);
  
  // Dispatch custom event for language change
  window.dispatchEvent(new CustomEvent('languageChanged', { 
    detail: { language: lang } 
  }));
}

/**
 * Initialize i18n system
 * Sets up language detection and event listeners
 */
function initializeI18n() {
  const currentLang = getCurrentLanguage();
  
  // Set initial language
  if (currentLang !== getLanguageFromURL()) {
    setLanguageInURL(currentLang);
  }
  
  // Add language change event listener
  window.addEventListener('languageChanged', (event) => {
    // Reload page to apply new language
    window.location.reload();
  });
}

// Export functions for use in other modules
module.exports = {
  getTranslation,
  getAvailableLanguages,
  isLanguageSupported,
  getLanguageDisplayName,
  getBrowserLanguage,
  getLanguageFromURL,
  setLanguageInURL,
  getLanguageFromStorage,
  setLanguageInStorage,
  getCurrentLanguage,
  changeLanguage,
  initializeI18n,
  defaultLanguage,
  translations
};

// For browser usage, also attach to window object
if (typeof window !== 'undefined') {
  window.i18n = {
    t: getTranslation,
    getAvailableLanguages,
    isLanguageSupported,
    getLanguageDisplayName,
    getBrowserLanguage,
    getLanguageFromURL,
    setLanguageInURL,
    getLanguageFromStorage,
    setLanguageInStorage,
    getCurrentLanguage,
    changeLanguage,
    initializeI18n,
    defaultLanguage
  };
}
