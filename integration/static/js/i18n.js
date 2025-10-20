// 다국어 지원 JavaScript 라이브러리
class I18n {
  constructor() {
    this.currentLanguage = localStorage.getItem('preferred_language') || 'ko';
    this.translations = {};
    this.loadTranslations();
  }

  async loadTranslations() {
    const languages = ['ko', 'en', 'ja', 'zh', 'ar', 'he', 'es', 'fr', 'de', 'ru'];
    
    for (const lang of languages) {
      try {
        const response = await fetch(`/i18n/locales/${lang}.json`);
        if (response.ok) {
          this.translations[lang] = await response.json();
        }
      } catch (error) {
        console.warn(`Failed to load translations for ${lang}:`, error);
      }
    }
  }

  t(key, variables = {}) {
    const keys = key.split('.');
    let value = this.translations[this.currentLanguage] || this.translations['ko'] || {};
    
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        // 한국어로 폴백
        value = this.translations['ko'] || {};
        for (const fallbackKey of keys) {
          if (value && typeof value === 'object' && fallbackKey in value) {
            value = value[fallbackKey];
          } else {
            return key; // 키를 찾을 수 없으면 키 자체 반환
          }
        }
        break;
      }
    }

    // 문자열 보간 처리
    if (typeof value === 'string' && Object.keys(variables).length > 0) {
      for (const [varName, varValue] of Object.entries(variables)) {
        value = value.replace(new RegExp(`{{${varName}}}`, 'g'), varValue);
      }
    }

    return value || key;
  }

  setLanguage(lang) {
    this.currentLanguage = lang;
    localStorage.setItem('preferred_language', lang);
    
    // RTL 언어 감지
    const isRTL = ['ar', 'he'].includes(lang);
    document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
    document.documentElement.lang = lang;
    
    // 페이지 새로고침
    window.location.reload();
  }

  getCurrentLanguage() {
    return this.currentLanguage;
  }

  getSupportedLanguages() {
    return [
      { code: 'ko', name: '한국어', flag: '🇰🇷' },
      { code: 'en', name: 'English', flag: '🇺🇸' },
      { code: 'ja', name: '日本語', flag: '🇯🇵' },
      { code: 'zh', name: '中文', flag: '🇨🇳' },
      { code: 'ar', name: 'العربية', flag: '🇸🇦' },
      { code: 'he', name: 'עברית', flag: '🇮🇱' },
      { code: 'es', name: 'Español', flag: '🇪🇸' },
      { code: 'fr', name: 'Français', flag: '🇫🇷' },
      { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
      { code: 'ru', name: 'Русский', flag: '🇷🇺' }
    ];
  }
}

// 전역 i18n 인스턴스 생성
window.i18n = new I18n();

// 언어 선택기 생성 함수
function createLanguageSelector() {
  const languages = window.i18n.getSupportedLanguages();
  const currentLang = window.i18n.getCurrentLanguage();
  const currentLangInfo = languages.find(lang => lang.code === currentLang) || languages[0];

  return `
    <div class="language-selector">
      <div class="dropdown">
        <button class="btn btn-outline-light dropdown-toggle" type="button" id="languageDropdown" data-bs-toggle="dropdown" aria-expanded="false">
          <span class="me-2">${currentLangInfo.flag}</span>
          <span>${currentLangInfo.name}</span>
        </button>
        <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="languageDropdown">
          ${languages.map(lang => `
            <li>
              <a class="dropdown-item ${lang.code === currentLang ? 'active' : ''}" 
                 href="#" 
                 onclick="window.i18n.setLanguage('${lang.code}')"
                 data-lang="${lang.code}">
                <span class="me-2">${lang.flag}</span>
                <span>${lang.name}</span>
              </a>
            </li>
          `).join('')}
        </ul>
      </div>
    </div>
  `;
}

// DOM이 로드된 후 언어 선택기 추가
document.addEventListener('DOMContentLoaded', function() {
  // 언어 선택기를 헤더에 추가
  const header = document.querySelector('.navbar');
  if (header) {
    const languageSelector = document.createElement('div');
    languageSelector.innerHTML = createLanguageSelector();
    header.appendChild(languageSelector.firstElementChild);
  }
  
  // 모든 번역 가능한 요소 업데이트
  updateTranslations();
});

// 번역 업데이트 함수
function updateTranslations() {
  // 제목 업데이트
  const titleElements = document.querySelectorAll('[data-i18n]');
  titleElements.forEach(element => {
    const key = element.getAttribute('data-i18n');
    element.textContent = window.i18n.t(key);
  });

  // 플레이스홀더 업데이트
  const placeholderElements = document.querySelectorAll('[data-i18n-placeholder]');
  placeholderElements.forEach(element => {
    const key = element.getAttribute('data-i18n-placeholder');
    element.placeholder = window.i18n.t(key);
  });

  // 툴팁 업데이트
  const tooltipElements = document.querySelectorAll('[data-i18n-title]');
  tooltipElements.forEach(element => {
    const key = element.getAttribute('data-i18n-title');
    element.title = window.i18n.t(key);
  });
}

// RTL 지원 CSS 추가
function addRTLSupport() {
  const style = document.createElement('style');
  style.textContent = `
    [dir="rtl"] {
      text-align: right;
    }
    
    [dir="rtl"] .navbar-nav {
      flex-direction: row-reverse;
    }
    
    [dir="rtl"] .dropdown-menu {
      text-align: right;
    }
    
    [dir="rtl"] .card-text {
      text-align: right;
    }
    
    [dir="rtl"] .btn-group {
      flex-direction: row-reverse;
    }
    
    [dir="rtl"] .d-flex {
      flex-direction: row-reverse;
    }
    
    [dir="rtl"] .text-start {
      text-align: right !important;
    }
    
    [dir="rtl"] .text-end {
      text-align: left !important;
    }
  `;
  document.head.appendChild(style);
}

// RTL 지원 CSS 추가
addRTLSupport();
