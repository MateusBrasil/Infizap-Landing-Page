"""Inject i18n runtime: detect language (URL/localStorage/IP), translate DOM, render switcher."""
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
    // Lusophone
    'BR':'pt-BR','PT':'pt-BR',
    // Hispanic
    'ES':'es','MX':'es','AR':'es','CL':'es','PE':'es','CO':'es','EC':'es',
    'VE':'es','UY':'es','PY':'es','BO':'es','CU':'es','DO':'es','GT':'es',
    'HN':'es','SV':'es','NI':'es','CR':'es','PA':'es',
    // Default: English for everywhere else
    'US':'en','GB':'en','CA':'en','AU':'en','NZ':'en','IE':'en','ZA':'en',
    'NL':'en','CH':'en','DE':'en','FR':'en','IT':'en','SA':'en','AE':'en',
    'IN':'en','SG':'en','PH':'en','MY':'en','JP':'en','KR':'en','CN':'en'
  };

  function normalizeLang(raw){
    if (!raw) return null;
    raw = String(raw).trim();
    if (raw === 'pt') return 'pt-BR';
    if (SUPPORTED[raw]) return raw;
    return null;
  }

  function detectFromUrl(){
    try {
      var p = new URLSearchParams(location.search);
      return normalizeLang(p.get('lang'));
    } catch(_){ return null; }
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

  function applyTranslations(dict){
    if (!dict) return;
    delete dict._meta;
    // Walk text nodes
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode: function(node){
        if (!node.parentNode) return NodeFilter.FILTER_REJECT;
        var tag = node.parentNode.nodeName;
        if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'NOSCRIPT') return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    }, false);
    var nodes = []; var n;
    while ((n = walker.nextNode())) nodes.push(n);
    nodes.forEach(function(node){
      var raw = node.nodeValue;
      var trimmed = raw.trim();
      if (!trimmed) return;
      var trans = dict[trimmed];
      if (trans && trans !== trimmed) {
        node.nodeValue = raw.replace(trimmed, trans);
      }
    });
    // Placeholders / aria-labels / title attrs
    var attrs = ['placeholder','aria-label','title','alt'];
    attrs.forEach(function(attr){
      var els = document.querySelectorAll('[' + attr + ']');
      Array.prototype.forEach.call(els, function(el){
        var v = (el.getAttribute(attr) || '').trim();
        if (v && dict[v]) el.setAttribute(attr, dict[v]);
      });
    });
  }

  function setHtmlLang(lang){
    try { document.documentElement.lang = (SUPPORTED[lang] && SUPPORTED[lang].html_lang) || lang; } catch(_){}
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
          '<span class="text-white/40 text-xs ml-auto">' + code + '</span>' +
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
      '<div id="lang-switcher-menu" style="display:none" class="absolute right-0 top-full mt-1.5 min-w-[140px] rounded-xl border border-white/10 bg-black/95 backdrop-blur-xl shadow-lg overflow-hidden z-50">' +
        menuHtml +
      '</div>';

    // Try to mount in the desktop navbar's flex row, right before/with the existing CTA.
    var navRow = document.querySelector('#mega-nav-wrapper > div.flex.h-14, #mega-nav-wrapper > div.flex.items-center.justify-between');
    if (!navRow) navRow = document.getElementById('mega-nav-wrapper');
    if (!navRow) return;
    // Insert before the rightmost child if possible (a flex justify-between layout)
    var rightmost = navRow.children[navRow.children.length - 1];
    if (rightmost && rightmost.tagName === 'BUTTON' && /menu/i.test(rightmost.id || '')) {
      // It's the mobile menu button; insert switcher before it
      navRow.insertBefore(wrap, rightmost);
    } else {
      navRow.appendChild(wrap);
    }
  }

  // Global click handler for switcher (delegated so it survives any DOM mutations)
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
    // Outside click: close menu
    var sw = e.target.closest && e.target.closest('#lang-switcher');
    if (!sw) {
      var menu2 = document.getElementById('lang-switcher-menu');
      if (menu2) menu2.style.display = 'none';
    }
  }, true);

  function apply(lang){
    setHtmlLang(lang);
    buildSwitcher(lang);
    if (lang === 'pt-BR') return; // default — nothing to translate
    fetch('/i18n/' + lang + '.json', {cache:'no-store'})
      .then(function(r){ return r.ok ? r.json() : null; })
      .then(function(dict){
        if (!dict) return;
        applyTranslations(dict);
      })
      .catch(function(){});
  }

  function init(){
    var picked = detectFromUrl() || detectFromStorage();
    if (picked) { apply(picked); return; }
    detectFromIP(function(country){
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
print(f'i18n script injected ({len(SCRIPT)} chars)')
print(f'file size: {len(c)}')
