/**
 * Language Selector Component
 * Provides a dropdown interface for language selection
 */

// Language selector HTML template
function createLanguageSelectorHTML(currentLang = 'ko') {
  const languages = {
    ko: { name: '한국어', flag: '🇰🇷' },
    en: { name: 'English', flag: '🇺🇸' },
    ja: { name: '日本語', flag: '🇯🇵' },
    zh: { name: '中文', flag: '🇨🇳' }
  };

  let optionsHTML = '';
  for (const [code, info] of Object.entries(languages)) {
    const selected = code === currentLang ? 'selected' : '';
    optionsHTML += `<option value="${code}" ${selected}>${info.flag} ${info.name}</option>`;
  }

  return `
    <div class="language-selector">
      <select id="languageSelect" class="form-select form-select-sm" onchange="changeLanguage(this.value)">
        ${optionsHTML}
      </select>
    </div>
  `;
}

// Language selector with Bootstrap styling
function createBootstrapLanguageSelector(currentLang = 'ko') {
  const languages = {
    ko: { name: '한국어', flag: '🇰🇷' },
    en: { name: 'English', flag: '🇺🇸' },
    ja: { name: '日本語', flag: '🇯🇵' },
    zh: { name: '中文', flag: '🇨🇳' }
  };

  let optionsHTML = '';
  for (const [code, info] of Object.entries(languages)) {
    const selected = code === currentLang ? 'selected' : '';
    optionsHTML += `<option value="${code}" ${selected}>${info.flag} ${info.name}</option>`;
  }

  return `
    <div class="dropdown">
      <button class="btn btn-outline-secondary dropdown-toggle" type="button" id="languageDropdown" data-bs-toggle="dropdown" aria-expanded="false">
        <i class="fas fa-globe"></i> ${languages[currentLang]?.flag || '🌐'} ${languages[currentLang]?.name || 'Language'}
      </button>
      <ul class="dropdown-menu" aria-labelledby="languageDropdown">
        ${Object.entries(languages).map(([code, info]) => `
          <li>
            <a class="dropdown-item ${code === currentLang ? 'active' : ''}" href="#" onclick="changeLanguage('${code}'); return false;">
              ${info.flag} ${info.name}
            </a>
          </li>
        `).join('')}
      </ul>
    </div>
  `;
}

// Compact language selector for navbar
function createNavbarLanguageSelector(currentLang = 'ko') {
  const languages = {
    ko: { name: '한국어', flag: '🇰🇷' },
    en: { name: 'English', flag: '🇺🇸' },
    ja: { name: '日本語', flag: '🇯🇵' },
    zh: { name: '中文', flag: '🇨🇳' }
  };

  return `
    <div class="navbar-language-selector">
      <div class="btn-group" role="group">
        ${Object.entries(languages).map(([code, info]) => `
          <button type="button" 
                  class="btn btn-sm ${code === currentLang ? 'btn-primary' : 'btn-outline-primary'}" 
                  onclick="changeLanguage('${code}')"
                  title="${info.name}">
            ${info.flag}
          </button>
        `).join('')}
      </div>
    </div>
  `;
}

// Language selector with custom styling
function createCustomLanguageSelector(currentLang = 'ko') {
  const languages = {
    ko: { name: '한국어', flag: '🇰🇷' },
    en: { name: 'English', flag: '🇺🇸' },
    ja: { name: '日本語', flag: '🇯🇵' },
    zh: { name: '中文', flag: '🇨🇳' }
  };

  return `
    <div class="custom-language-selector">
      <div class="language-toggle">
        <span class="current-language">
          <span class="flag">${languages[currentLang]?.flag || '🌐'}</span>
          <span class="name">${languages[currentLang]?.name || 'Language'}</span>
          <i class="fas fa-chevron-down"></i>
        </span>
        <div class="language-options">
          ${Object.entries(languages).map(([code, info]) => `
            <div class="language-option ${code === currentLang ? 'active' : ''}" 
                 onclick="changeLanguage('${code}')">
              <span class="flag">${info.flag}</span>
              <span class="name">${info.name}</span>
            </div>
          `).join('')}
        </div>
      </div>
    </div>
    
    <style>
      .custom-language-selector {
        position: relative;
        display: inline-block;
      }
      
      .language-toggle {
        cursor: pointer;
        padding: 8px 12px;
        border: 1px solid #ddd;
        border-radius: 6px;
        background: white;
        display: flex;
        align-items: center;
        gap: 8px;
        transition: all 0.3s ease;
      }
      
      .language-toggle:hover {
        border-color: #007bff;
        box-shadow: 0 2px 4px rgba(0,123,255,0.1);
      }
      
      .current-language {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 14px;
      }
      
      .flag {
        font-size: 16px;
      }
      
      .language-options {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid #ddd;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        z-index: 1000;
        display: none;
        margin-top: 4px;
      }
      
      .language-option {
        padding: 10px 12px;
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
        transition: background-color 0.2s ease;
        font-size: 14px;
      }
      
      .language-option:hover {
        background-color: #f8f9fa;
      }
      
      .language-option.active {
        background-color: #e3f2fd;
        color: #1976d2;
      }
      
      .custom-language-selector:hover .language-options {
        display: block;
      }
    </style>
  `;
}

// Language change function
function changeLanguage(langCode) {
  if (typeof window !== 'undefined' && window.i18n) {
    window.i18n.changeLanguage(langCode);
  } else {
    // Fallback: direct URL change
    const url = new URL(window.location);
    url.searchParams.set('lang', langCode);
    window.location.href = url.toString();
  }
}

// Initialize language selector
function initializeLanguageSelector(selectorId = 'languageSelector', currentLang = 'ko', style = 'bootstrap') {
  const selector = document.getElementById(selectorId);
  if (!selector) return;

  let html = '';
  switch (style) {
    case 'bootstrap':
      html = createBootstrapLanguageSelector(currentLang);
      break;
    case 'navbar':
      html = createNavbarLanguageSelector(currentLang);
      break;
    case 'custom':
      html = createCustomLanguageSelector(currentLang);
      break;
    default:
      html = createLanguageSelectorHTML(currentLang);
  }

  selector.innerHTML = html;
}

// Auto-detect current language from URL or localStorage
function getCurrentLanguageFromPage() {
  // Try to get from URL parameter
  const urlParams = new URLSearchParams(window.location.search);
  const urlLang = urlParams.get('lang');
  if (urlLang && ['ko', 'en', 'ja', 'zh'].includes(urlLang)) {
    return urlLang;
  }

  // Try to get from localStorage
  const storedLang = localStorage.getItem('language');
  if (storedLang && ['ko', 'en', 'ja', 'zh'].includes(storedLang)) {
    return storedLang;
  }

  // Try to get from browser language
  const browserLang = navigator.language.split('-')[0];
  if (['ko', 'en', 'ja', 'zh'].includes(browserLang)) {
    return browserLang;
  }

  // Default to Korean
  return 'ko';
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    createLanguageSelectorHTML,
    createBootstrapLanguageSelector,
    createNavbarLanguageSelector,
    createCustomLanguageSelector,
    changeLanguage,
    initializeLanguageSelector,
    getCurrentLanguageFromPage
  };
}

// For browser usage, attach to window object
if (typeof window !== 'undefined') {
  window.LanguageSelector = {
    createHTML: createLanguageSelectorHTML,
    createBootstrap: createBootstrapLanguageSelector,
    createNavbar: createNavbarLanguageSelector,
    createCustom: createCustomLanguageSelector,
    changeLanguage,
    initialize: initializeLanguageSelector,
    getCurrentLanguage: getCurrentLanguageFromPage
  };
}
