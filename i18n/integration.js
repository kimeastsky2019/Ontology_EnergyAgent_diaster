/**
 * i18n Integration Helper for Web Interface
 * Provides functions to integrate i18n with existing web interface
 */

// Load translation files
const translations = {
  ko: require('./locales/ko.json'),
  en: require('./locales/en.json'),
  ja: require('./locales/ja.json'),
  zh: require('./locales/zh.json')
};

/**
 * Get translation for a given key and language
 * @param {string} key - Translation key
 * @param {string} lang - Language code
 * @param {object} variables - Variables to interpolate
 * @returns {string} Translated text
 */
function t(key, lang = 'ko', variables = {}) {
  const langData = translations[lang] || translations['ko'];
  
  // Navigate through nested object using dot notation
  const keys = key.split('.');
  let value = langData;
  
  for (const k of keys) {
    if (value && typeof value === 'object' && k in value) {
      value = value[k];
    } else {
      // Fallback to Korean if key not found
      const koData = translations['ko'];
      let fallbackValue = koData;
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
 * Get current language from URL parameter
 * @returns {string} Current language code
 */
function getCurrentLanguage() {
  const urlParams = new URLSearchParams(window.location.search);
  const langParam = urlParams.get('lang');
  return ['ko', 'en', 'ja', 'zh'].includes(langParam) ? langParam : 'ko';
}

/**
 * Generate language selector HTML
 * @param {string} currentLang - Current language
 * @returns {string} HTML for language selector
 */
function generateLanguageSelector(currentLang = 'ko') {
  const languages = {
    ko: { name: '한국어', flag: '🇰🇷' },
    en: { name: 'English', flag: '🇺🇸' },
    ja: { name: '日本語', flag: '🇯🇵' },
    zh: { name: '中文', flag: '🇨🇳' }
  };

  return `
    <div class="language-selector">
      <div class="btn-group" role="group">
        ${Object.entries(languages).map(([code, info]) => `
          <a href="?lang=${code}" 
             class="btn btn-sm ${code === currentLang ? 'btn-primary' : 'btn-outline-primary'}"
             title="${info.name}">
            ${info.flag}
          </a>
        `).join('')}
      </div>
    </div>
  `;
}

/**
 * Generate navigation menu with translations
 * @param {string} currentLang - Current language
 * @returns {string} HTML for navigation menu
 */
function generateNavigation(currentLang = 'ko') {
  return `
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container-fluid">
        <a class="navbar-brand" href="/?lang=${currentLang}">
          <i class="fas fa-bolt"></i> ${t('title', currentLang)}
        </a>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <a class="nav-link" href="/?lang=${currentLang}">
                <i class="fas fa-home"></i> ${t('navigation.home', currentLang)}
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/data-collection?lang=${currentLang}">
                <i class="fas fa-solar-panel"></i> ${t('navigation.energySupply', currentLang)}
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/data-analysis?lang=${currentLang}">
                <i class="fas fa-chart-line"></i> ${t('navigation.energyDemand', currentLang)}
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/model-testing?lang=${currentLang}">
                <i class="fas fa-brain"></i> ${t('navigation.modelTesting', currentLang)}
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/statistics?lang=${currentLang}">
                <i class="fas fa-cogs"></i> ${t('navigation.demandControl', currentLang)}
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/health?lang=${currentLang}">
                <i class="fas fa-heartbeat"></i> ${t('navigation.health', currentLang)}
              </a>
            </li>
          </ul>
          
          <div class="navbar-nav">
            ${generateLanguageSelector(currentLang)}
          </div>
        </div>
      </div>
    </nav>
  `;
}

/**
 * Replace text content with translations
 * @param {string} currentLang - Current language
 */
function translatePageContent(currentLang = 'ko') {
  // Find all elements with data-translate attribute
  const elements = document.querySelectorAll('[data-translate]');
  
  elements.forEach(element => {
    const key = element.getAttribute('data-translate');
    const translatedText = t(key, currentLang);
    
    if (translatedText && translatedText !== key) {
      element.textContent = translatedText;
    }
  });
  
  // Find all elements with data-translate-html attribute
  const htmlElements = document.querySelectorAll('[data-translate-html]');
  
  htmlElements.forEach(element => {
    const key = element.getAttribute('data-translate-html');
    const translatedText = t(key, currentLang);
    
    if (translatedText && translatedText !== key) {
      element.innerHTML = translatedText;
    }
  });
}

/**
 * Initialize i18n for the page
 * @param {string} currentLang - Current language
 */
function initializeI18n(currentLang = 'ko') {
  // Set page title
  document.title = t('title', currentLang);
  
  // Translate page content
  translatePageContent(currentLang);
  
  // Add language change event listener
  window.addEventListener('languageChanged', (event) => {
    const newLang = event.detail.language;
    translatePageContent(newLang);
    document.title = t('title', newLang);
  });
}

/**
 * Create translation helper for use in templates
 * @param {string} currentLang - Current language
 * @returns {function} Translation function
 */
function createTranslationHelper(currentLang = 'ko') {
  return (key, variables = {}) => t(key, currentLang, variables);
}

// Export functions
module.exports = {
  t,
  getCurrentLanguage,
  generateLanguageSelector,
  generateNavigation,
  translatePageContent,
  initializeI18n,
  createTranslationHelper,
  translations
};

// For browser usage, attach to window object
if (typeof window !== 'undefined') {
  window.i18nHelper = {
    t,
    getCurrentLanguage,
    generateLanguageSelector,
    generateNavigation,
    translatePageContent,
    initializeI18n,
    createTranslationHelper
  };
}
