"""V2 i18n runtime — more robust matching + diagnostic + hamburger placement fix."""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

p = Path('infizap-lp-v1.html')
c = p.read_text(encoding='utf-8')

SCRIPT = r"""
<script>
(function(){
  'use strict';

  var SUPPORTED = {
    'pt-BR': { name:'PT', flag:'br', html_lang:'pt-BR' },
    'en':    { name:'EN', flag:'us', html_lang:'en'    },
    'es':    { name:'ES', flag:'es', html_lang:'es'    }
  };

  var COUNTRY_TO_LANG = {
    'BR':'pt-BR','PT':'pt-BR',
    'ES':'es','MX':'es','AR':'es','CL':'es','PE':'es','CO':'es','EC':'es',
    'VE':'es','UY':'es','PY':'es','BO':'es','CU':'es','DO':'es','GT':'es',
    'HN':'es','SV':'es','NI':'es','CR':'es','PA':'es',
    'US':'en','GB':'en','CA':'en','AU':'en','NZ':'en','IE':'en','ZA':'en',
    'NL':'en','CH':'en','DE':'en','FR':'en','IT':'en','SA':'en','AE':'en',
    'IN':'en','SG':'en','PH':'en','MY':'en','JP':'en','KR':'en','CN':'en'
  };

  // Diagnostic flag — inspect via console: window.__INFIZAP_I18N
  window.__INFIZAP_I18N = { stage:'init' };

  function normalizeLang(raw){
    if (!raw) return null;
    raw = String(raw).trim();
    if (raw === 'pt') return 'pt-BR';
    if (SUPPORTED[raw]) return raw;
    return null;
  }
  function detectFromUrl(){
    try { return normalizeLang(new URLSearchParams(location.search).get('lang')); } catch(_){ return null; }
  }
  function detectFromStorage(){
    try { return normalizeLang(localStorage.getItem('infizap_lang')); } catch(_){ return null; }
  }
  function detectFromIP(cb){
    var services = [
      { url:'https://ipapi.co/json/', key:'country_code' },
      { url:'https://api.country.is/', key:'country' }
    ];
    var done = false;
    services.forEach(function(svc){
      fetch(svc.url, {cache:'no-store'})
        .then(function(r){ return r.ok ? r.json() : null; })
        .then(function(data){
          if (done || !data) return;
          var cc = String(data[svc.key]||'').toUpperCase();
          if (cc) { done = true; cb(cc); }
        })
        .catch(function(){});
    });
    setTimeout(function(){ if (!done) { done = true; cb(null); } }, 4000);
  }

  function setHtmlLang(lang){
    try { document.documentElement.lang = (SUPPORTED[lang] && SUPPORTED[lang].html_lang) || lang; } catch(_){}
  }

  // Apply translations by walking text nodes + replacing in attributes.
  // More defensive than v1: catches DOM mutation by re-running after delays.
  function applyTranslations(dict){
    if (!dict) return 0;
    var keysExisted = Object.keys(dict).length;
    delete dict._meta;
    var dictKeys = Object.keys(dict);
    if (!dictKeys.length) return 0;

    var replaced = 0;
    // Pass 1: text nodes via querySelectorAll (more reliable than TreeWalker)
    var TAGS = 'h1,h2,h3,h4,h5,h6,p,span,button,a,label,li,td,th,strong,em,small,b,div,figcaption,blockquote';
    var elements = document.querySelectorAll(TAGS);
    Array.prototype.forEach.call(elements, function(el){
      // For each direct text-node child, attempt to match-and-replace
      var i; var children = el.childNodes;
      for (i = 0; i < children.length; i++) {
        var node = children[i];
        if (node.nodeType !== 3) continue; // text node only
        var raw = node.nodeValue;
        var trimmed = raw.trim();
        if (!trimmed) continue;
        if (dict.hasOwnProperty(trimmed)) {
          var t = dict[trimmed];
          if (t && t !== trimmed) {
            node.nodeValue = raw.replace(trimmed, t);
            replaced++;
          }
        }
      }
    });
    // Pass 2: attribute translations
    ['placeholder','aria-label','title','alt'].forEach(function(attr){
      var attrEls = document.querySelectorAll('[' + attr + ']');
      Array.prototype.forEach.call(attrEls, function(el){
        var v = (el.getAttribute(attr) || '').trim();
        if (v && dict.hasOwnProperty(v)) {
          var t = dict[v];
          if (t && t !== v) {
            el.setAttribute(attr, t);
            replaced++;
          }
        }
      });
    });
    return replaced;
  }

  function buildSwitcher(currentLang){
    if (document.getElementById('lang-switcher')) return;
    var current = SUPPORTED[currentLang] || SUPPORTED['pt-BR'];
    var menuHtml = '';
    Object.keys(SUPPORTED).forEach(function(code){
      var s = SUPPORTED[code];
      menuHtml +=
        '<button type="button" data-lang="' + code + '" class="flex items-center gap-2 w-full px-3 py-2 text-sm text-white hover:bg-white/10 text-left">' +
          '<img src="https://flagcdn.com/w40/' + s.flag + '.png" alt="" width="18" height="13" class="rounded-sm shrink-0" style="object-fit:cover">' +
          '<span class="font-medium">' + s.name + '</span>' +
        '</button>';
    });
    var wrap = document.createElement('div');
    wrap.id = 'lang-switcher';
    wrap.className = 'relative shrink-0';
    wrap.innerHTML =
      '<button type="button" id="lang-switcher-btn" aria-label="Idioma" class="inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 hover:bg-white/10 px-3 h-9 text-sm text-white transition-colors">' +
        '<img src="https://flagcdn.com/w40/' + current.flag + '.png" alt="" width="18" height="13" class="rounded-sm" style="object-fit:cover">' +
        '<span class="font-semibold">' + current.name + '</span>' +
        '<svg viewBox="0 0 20 20" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" class="opacity-60"><polyline points="6 9 12 15 18 9"/></svg>' +
      '</button>' +
      '<div id="lang-switcher-menu" style="display:none" class="absolute right-0 top-full mt-1.5 min-w-[120px] rounded-xl border border-white/10 bg-black/95 backdrop-blur-xl shadow-lg overflow-hidden z-50">' +
        menuHtml +
      '</div>';

    // PLACEMENT: insert switcher BEFORE the hamburger button so the hamburger ends up rightmost.
    var hamburger = document.getElementById('mobile-menu-btn');
    if (hamburger && hamburger.parentNode) {
      hamburger.parentNode.insertBefore(wrap, hamburger);
    } else {
      var navRow = document.querySelector('#mega-nav-wrapper > div.flex');
      if (navRow) navRow.appendChild(wrap);
      else (document.getElementById('mega-nav-wrapper') || document.body).appendChild(wrap);
    }
  }

  // Delegated click handler for switcher (capture phase, survives DOM mutations)
  document.addEventListener('click', function(e){
    var btn = e.target.closest && e.target.closest('#lang-switcher-btn');
    if (btn) {
      e.preventDefault(); e.stopPropagation();
      var menu = document.getElementById('lang-switcher-menu');
      if (menu) menu.style.display = (menu.style.display === 'none' || !menu.style.display) ? 'block' : 'none';
      return;
    }
    var item = e.target.closest && e.target.closest('#lang-switcher-menu button[data-lang]');
    if (item) {
      e.preventDefault();
      var newLang = item.getAttribute('data-lang');
      try { localStorage.setItem('infizap_lang', newLang); } catch(_){}
      var url = new URL(location.href);
      url.searchParams.set('lang', newLang);
      location.href = url.toString();
      return;
    }
    var sw = e.target.closest && e.target.closest('#lang-switcher');
    if (!sw) {
      var menu2 = document.getElementById('lang-switcher-menu');
      if (menu2) menu2.style.display = 'none';
    }
  }, true);

  function apply(lang){
    window.__INFIZAP_I18N.lang = lang;
    setHtmlLang(lang);
    buildSwitcher(lang);
    if (lang === 'pt-BR') {
      window.__INFIZAP_I18N.stage = 'pt-default';
      return;
    }
    window.__INFIZAP_I18N.stage = 'fetching';
    fetch('/i18n/' + lang + '.json', {cache:'no-store'})
      .then(function(r){
        window.__INFIZAP_I18N.fetchStatus = r.status;
        return r.ok ? r.json() : null;
      })
      .then(function(dict){
        if (!dict) { window.__INFIZAP_I18N.stage = 'no-dict'; return; }
        window.__INFIZAP_I18N.dictKeys = Object.keys(dict).length;
        var first = applyTranslations(dict);
        window.__INFIZAP_I18N.firstPass = first;
        // Re-run after delays — catches DOM that got injected by other scripts
        setTimeout(function(){ var n = applyTranslations(dict); window.__INFIZAP_I18N.secondPass = n; }, 500);
        setTimeout(function(){ var n = applyTranslations(dict); window.__INFIZAP_I18N.thirdPass = n; }, 1500);
        window.__INFIZAP_I18N.stage = 'applied';
      })
      .catch(function(err){
        window.__INFIZAP_I18N.stage = 'fetch-error';
        window.__INFIZAP_I18N.error = String(err);
      });
  }

  function init(){
    var picked = detectFromUrl() || detectFromStorage();
    if (picked) { apply(picked); return; }
    detectFromIP(function(country){
      window.__INFIZAP_I18N.ipCountry = country || 'unknown';
      var lang = (country && COUNTRY_TO_LANG[country]) || 'pt-BR';
      apply(lang);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
</script>
"""

body_end = c.rfind('</body>')
if body_end < 0:
    print('ERROR: </body> not found')
    sys.exit(1)
c = c[:body_end] + SCRIPT + c[body_end:]
p.write_text(c, encoding='utf-8')
print(f'v2 i18n script injected ({len(SCRIPT)} chars)')
print(f'file size: {len(c)}')
