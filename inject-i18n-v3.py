"""V3 i18n runtime — dicts EMBEDDED inline (no fetch), aggressive multi-pass."""
import sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

# Load dictionaries
en = json.loads(Path('i18n/en.json').read_text(encoding='utf-8'))
es = json.loads(Path('i18n/es.json').read_text(encoding='utf-8'))
en.pop('_meta', None)
es.pop('_meta', None)
print(f'EN entries: {len(en)}')
print(f'ES entries: {len(es)}')

EN_JSON = json.dumps(en, ensure_ascii=False)
ES_JSON = json.dumps(es, ensure_ascii=False)

# Remove old i18n script
p = Path('infizap-lp-v1.html')
c = p.read_text(encoding='utf-8')
start = c.find("\n<script>\n(function(){\n  'use strict';\n\n  var SUPPORTED = {")
if start < 0:
    print('ERROR: old script marker not found')
    sys.exit(1)
end = c.find('</script>', start) + len('</script>')
c = c[:start+1] + c[end:]
print(f'old script removed, current size: {len(c)}')

# Build new script with dicts embedded
SCRIPT_BODY = """
<script>
(function(){
  "use strict";
  var EN = __EN_JSON__;
  var ES = __ES_JSON__;
  var DICTS = { "en": EN, "es": ES };

  var SUPPORTED = {
    "pt-BR": { name:"PT", flag:"br", html_lang:"pt-BR" },
    "en":    { name:"EN", flag:"us", html_lang:"en"    },
    "es":    { name:"ES", flag:"es", html_lang:"es"    }
  };
  var COUNTRY_TO_LANG = {
    "BR":"pt-BR","PT":"pt-BR",
    "ES":"es","MX":"es","AR":"es","CL":"es","PE":"es","CO":"es","EC":"es",
    "VE":"es","UY":"es","PY":"es","BO":"es","CU":"es","DO":"es","GT":"es",
    "HN":"es","SV":"es","NI":"es","CR":"es","PA":"es",
    "US":"en","GB":"en","CA":"en","AU":"en","NZ":"en","IE":"en","ZA":"en",
    "NL":"en","CH":"en","DE":"en","FR":"en","IT":"en","SA":"en","AE":"en",
    "IN":"en","SG":"en","PH":"en","MY":"en","JP":"en","KR":"en","CN":"en"
  };

  window.__INFIZAP_I18N = { stage:"boot" };

  function norm(raw){
    if (!raw) return null;
    raw = String(raw).trim();
    if (raw === "pt") return "pt-BR";
    return SUPPORTED[raw] ? raw : null;
  }
  function fromUrl(){ try { return norm(new URLSearchParams(location.search).get("lang")); } catch(_){ return null; } }
  function fromStorage(){ try { return norm(localStorage.getItem("infizap_lang")); } catch(_){ return null; } }
  function fromIP(cb){
    var done = false;
    [{u:"https://ipapi.co/json/",k:"country_code"},{u:"https://api.country.is/",k:"country"}].forEach(function(s){
      fetch(s.u,{cache:"no-store"}).then(function(r){return r.ok?r.json():null;}).then(function(d){
        if (done||!d) return;
        var cc=String(d[s.k]||"").toUpperCase();
        if (cc){ done=true; cb(cc); }
      }).catch(function(){});
    });
    setTimeout(function(){ if (!done){ done=true; cb(null); } }, 4000);
  }

  function applyTranslations(dict){
    if (!dict) return 0;
    var replaced = 0;
    var all = document.getElementsByTagName("*");
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      var tag = el.tagName;
      if (tag === "SCRIPT" || tag === "STYLE" || tag === "NOSCRIPT") continue;
      var ch = el.childNodes;
      for (var j = 0; j < ch.length; j++) {
        var node = ch[j];
        if (node.nodeType !== 3) continue;
        var raw = node.nodeValue;
        if (!raw) continue;
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
    }
    ["placeholder","aria-label","title","alt"].forEach(function(attr){
      var els = document.querySelectorAll("[" + attr + "]");
      for (var k = 0; k < els.length; k++) {
        var v = (els[k].getAttribute(attr) || "").trim();
        if (v && dict.hasOwnProperty(v)) {
          var t = dict[v];
          if (t && t !== v) {
            els[k].setAttribute(attr, t);
            replaced++;
          }
        }
      }
    });
    return replaced;
  }

  function buildSwitcher(currentLang){
    if (document.getElementById("lang-switcher")) return;
    var cur = SUPPORTED[currentLang] || SUPPORTED["pt-BR"];
    var menu = "";
    Object.keys(SUPPORTED).forEach(function(code){
      var s = SUPPORTED[code];
      menu += '<button type="button" data-lang="' + code + '" class="flex items-center gap-2 w-full px-3 py-2 text-sm text-white hover:bg-white/10 text-left"><img src="https://flagcdn.com/w40/' + s.flag + '.png" alt="" width="18" height="13" class="rounded-sm shrink-0" style="object-fit:cover"><span class="font-medium">' + s.name + '</span></button>';
    });
    var wrap = document.createElement("div");
    wrap.id = "lang-switcher";
    wrap.className = "relative shrink-0";
    wrap.innerHTML =
      '<button type="button" id="lang-switcher-btn" aria-label="Idioma" class="inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 hover:bg-white/10 px-3 h-9 text-sm text-white transition-colors">' +
        '<img src="https://flagcdn.com/w40/' + cur.flag + '.png" alt="" width="18" height="13" class="rounded-sm" style="object-fit:cover">' +
        '<span class="font-semibold">' + cur.name + '</span>' +
        '<svg viewBox="0 0 20 20" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" class="opacity-60"><polyline points="6 9 12 15 18 9"/></svg>' +
      '</button>' +
      '<div id="lang-switcher-menu" style="display:none" class="absolute right-0 top-full mt-1.5 min-w-[120px] rounded-xl border border-white/10 bg-black/95 backdrop-blur-xl shadow-lg overflow-hidden z-50">' + menu + '</div>';
    var hb = document.getElementById("mobile-menu-btn");
    if (hb && hb.parentNode) hb.parentNode.insertBefore(wrap, hb);
    else (document.querySelector("#mega-nav-wrapper > div.flex") || document.getElementById("mega-nav-wrapper") || document.body).appendChild(wrap);
  }

  document.addEventListener("click", function(e){
    var btn = e.target.closest && e.target.closest("#lang-switcher-btn");
    if (btn){ e.preventDefault(); e.stopPropagation(); var m=document.getElementById("lang-switcher-menu"); if (m) m.style.display = (m.style.display==="none"||!m.style.display) ? "block" : "none"; return; }
    var item = e.target.closest && e.target.closest("#lang-switcher-menu button[data-lang]");
    if (item){ e.preventDefault(); var nl=item.getAttribute("data-lang"); try{localStorage.setItem("infizap_lang", nl);}catch(_){} var u=new URL(location.href); u.searchParams.set("lang", nl); location.href = u.toString(); return; }
    if (!(e.target.closest && e.target.closest("#lang-switcher"))){ var m2=document.getElementById("lang-switcher-menu"); if (m2) m2.style.display="none"; }
  }, true);

  function go(lang){
    window.__INFIZAP_I18N.lang = lang;
    try { document.documentElement.lang = (SUPPORTED[lang] && SUPPORTED[lang].html_lang) || lang; } catch(_){}
    buildSwitcher(lang);
    if (lang === "pt-BR") { window.__INFIZAP_I18N.stage = "pt-default"; return; }
    var dict = DICTS[lang];
    if (!dict) { window.__INFIZAP_I18N.stage = "no-dict"; return; }
    window.__INFIZAP_I18N.dictKeys = Object.keys(dict).length;
    var pass1 = applyTranslations(dict);
    window.__INFIZAP_I18N.pass1 = pass1;
    var passes = [];
    var ticks = 0;
    var ticker = setInterval(function(){
      ticks++;
      var n = applyTranslations(dict);
      passes.push(n);
      if (ticks >= 20) { clearInterval(ticker); window.__INFIZAP_I18N.passes = passes; window.__INFIZAP_I18N.stage = "applied"; }
    }, 200);
  }

  function init(){
    var picked = fromUrl() || fromStorage();
    if (picked) { go(picked); return; }
    fromIP(function(country){
      window.__INFIZAP_I18N.ipCountry = country || "unknown";
      var lang = (country && COUNTRY_TO_LANG[country]) || "pt-BR";
      go(lang);
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
</script>
"""

SCRIPT = SCRIPT_BODY.replace('__EN_JSON__', EN_JSON).replace('__ES_JSON__', ES_JSON)

body_end = c.rfind('</body>')
c = c[:body_end] + SCRIPT + c[body_end:]
p.write_text(c, encoding='utf-8')
print(f'v3 injected ({len(SCRIPT)} chars, dicts embedded inline)')
print(f'final file size: {len(c)}')
