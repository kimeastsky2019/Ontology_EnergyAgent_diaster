import React from 'react';
import { useTranslation } from 'react-i18next';
import './LanguageSelector.css';

const LanguageSelector = () => {
  const { i18n, t } = useTranslation();

  const languages = [
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

  const currentLanguage = languages.find(lang => lang.code === i18n.language) || languages[0];

  const changeLanguage = (languageCode) => {
    i18n.changeLanguage(languageCode);
    // RTL 언어 감지 및 HTML dir 속성 설정
    const isRTL = ['ar', 'he'].includes(languageCode);
    document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
    document.documentElement.lang = languageCode;
  };

  return (
    <div className="language-selector">
      <div className="dropdown">
        <button 
          className="dropdown-toggle"
          type="button"
          id="languageDropdown"
          data-bs-toggle="dropdown"
          aria-expanded="false"
        >
          <span className="flag">{currentLanguage.flag}</span>
          <span className="language-name">{currentLanguage.name}</span>
          <i className="fas fa-chevron-down"></i>
        </button>
        <ul className="dropdown-menu" aria-labelledby="languageDropdown">
          {languages.map((language) => (
            <li key={language.code}>
              <button
                className={`dropdown-item ${i18n.language === language.code ? 'active' : ''}`}
                onClick={() => changeLanguage(language.code)}
                type="button"
              >
                <span className="flag">{language.flag}</span>
                <span className="language-name">{language.name}</span>
                {i18n.language === language.code && (
                  <i className="fas fa-check"></i>
                )}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default LanguageSelector;
