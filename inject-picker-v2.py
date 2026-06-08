"""Inject improved picker with event delegation + navigator.language priority."""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

p = Path('infizap-lp-v1.html')
c = p.read_text(encoding='utf-8')

COUNTRIES = [
    ('ZA','+27','África do Sul'),       ('DE','+49','Alemanha'),
    ('SA','+966','Arábia Saudita'),     ('AR','+54','Argentina'),
    ('AU','+61','Austrália'),           ('AT','+43','Áustria'),
    ('BE','+32','Bélgica'),             ('BO','+591','Bolívia'),
    ('BR','+55','Brasil'),              ('BG','+359','Bulgária'),
    ('CA','+1','Canadá'),               ('QA','+974','Catar'),
    ('CL','+56','Chile'),               ('CN','+86','China'),
    ('CY','+357','Chipre'),             ('CO','+57','Colômbia'),
    ('KR','+82','Coreia do Sul'),       ('CR','+506','Costa Rica'),
    ('HR','+385','Croácia'),            ('CU','+53','Cuba'),
    ('DK','+45','Dinamarca'),           ('EG','+20','Egito'),
    ('SV','+503','El Salvador'),        ('AE','+971','Emirados Árabes'),
    ('EC','+593','Equador'),            ('SK','+421','Eslováquia'),
    ('SI','+386','Eslovênia'),          ('ES','+34','Espanha'),
    ('US','+1','Estados Unidos'),       ('EE','+372','Estônia'),
    ('PH','+63','Filipinas'),           ('FI','+358','Finlândia'),
    ('FR','+33','França'),               ('GR','+30','Grécia'),
    ('GT','+502','Guatemala'),          ('NL','+31','Holanda'),
    ('HN','+504','Honduras'),           ('HU','+36','Hungria'),
    ('IN','+91','Índia'),               ('ID','+62','Indonésia'),
    ('IE','+353','Irlanda'),            ('IL','+972','Israel'),
    ('IT','+39','Itália'),              ('JP','+81','Japão'),
    ('LV','+371','Letônia'),            ('LT','+370','Lituânia'),
    ('LU','+352','Luxemburgo'),         ('MY','+60','Malásia'),
    ('MT','+356','Malta'),              ('MA','+212','Marrocos'),
    ('MX','+52','México'),              ('NI','+505','Nicarágua'),
    ('NO','+47','Noruega'),             ('NZ','+64','Nova Zelândia'),
    ('PA','+507','Panamá'),             ('PY','+595','Paraguai'),
    ('PE','+51','Peru'),                ('PL','+48','Polônia'),
    ('PT','+351','Portugal'),           ('GB','+44','Reino Unido'),
    ('DO','+1809','República Dominicana'), ('CZ','+420','República Tcheca'),
    ('RO','+40','Romênia'),             ('RU','+7','Rússia'),
    ('SG','+65','Singapura'),           ('SE','+46','Suécia'),
    ('CH','+41','Suíça'),               ('TH','+66','Tailândia'),
    ('TW','+886','Taiwan'),             ('TR','+90','Turquia'),
    ('UA','+380','Ucrânia'),            ('UY','+598','Uruguai'),
    ('VE','+58','Venezuela'),           ('VN','+84','Vietnã'),
]
js_arr = '[' + ','.join(
    "{code:'%s',dial:'%s',name:'%s'}" % (code, dial, name)
    for code, dial, name in COUNTRIES
) + ']'

NEW_SCRIPT = """
<script>
(function(){
  var COUNTRIES = """ + js_arr + """;

  var LANG_TO_COUNTRY = {
    'pt-br':'BR','pt':'BR','pt-pt':'PT',
    'es-es':'ES','es-mx':'MX','es-ar':'AR','es-co':'CO','es-cl':'CL',
    'es-pe':'PE','es-ec':'EC','es-ve':'VE','es-uy':'UY','es-py':'PY',
    'es-bo':'BO','es-cu':'CU','es-do':'DO','es-gt':'GT','es-hn':'HN',
    'es-sv':'SV','es-ni':'NI','es-cr':'CR','es-pa':'PA','es':'ES',
    'en-us':'US','en-gb':'GB','en-ca':'CA','en-au':'AU','en-nz':'NZ',
    'en-ie':'IE','en-za':'ZA','en':'US',
    'fr-fr':'FR','fr-ca':'CA','fr-be':'BE','fr-ch':'CH','fr':'FR',
    'de-de':'DE','de-at':'AT','de-ch':'CH','de':'DE',
    'it-it':'IT','it':'IT',
    'nl-nl':'NL','nl-be':'BE','nl':'NL',
    'sv-se':'SE','sv':'SE',
    'da-dk':'DK','da':'DK',
    'no-no':'NO','nb-no':'NO','no':'NO',
    'fi-fi':'FI','fi':'FI',
    'pl-pl':'PL','pl':'PL',
    'cs-cz':'CZ','cs':'CZ',
    'sk-sk':'SK','sk':'SK',
    'hu-hu':'HU','hu':'HU',
    'ro-ro':'RO','ro':'RO',
    'bg-bg':'BG','bg':'BG',
    'el-gr':'GR','el':'GR',
    'tr-tr':'TR','tr':'TR',
    'uk-ua':'UA','uk':'UA',
    'ru-ru':'RU','ru':'RU',
    'he-il':'IL','he':'IL',
    'ar-sa':'SA','ar-ae':'AE','ar-eg':'EG','ar-ma':'MA','ar':'SA',
    'ja-jp':'JP','ja':'JP',
    'ko-kr':'KR','ko':'KR',
    'zh-cn':'CN','zh-tw':'TW','zh':'CN',
    'th-th':'TH','th':'TH',
    'vi-vn':'VN','vi':'VN',
    'id-id':'ID','id':'ID',
    'ms-my':'MY','ms':'MY',
    'hi-in':'IN','hi':'IN'
  };

  function findCountry(code) {
    code = (code || '').toUpperCase();
    for (var i = 0; i < COUNTRIES.length; i++) {
      if (COUNTRIES[i].code === code) return COUNTRIES[i];
    }
    return null;
  }

  function flagImg(code) {
    var src = 'https://flagcdn.com/w40/' + code.toLowerCase() + '.png';
    return '<img src="' + src + '" alt="" width="20" height="14" class="rounded-sm" style="object-fit:cover;display:inline-block;vertical-align:middle">';
  }

  function applyCountryTo(flagId, codeId, country) {
    var fe = document.getElementById(flagId);
    var ce = document.getElementById(codeId);
    if (fe) fe.innerHTML = flagImg(country.code);
    if (ce) ce.textContent = country.dial;
  }

  function applyDefault(country) {
    applyCountryTo('cp-country-flag', 'cp-country-code', country);
    applyCountryTo('demo-country-flag', 'demo-country-code', country);
    window.demoSelectedDial = country.dial;
  }

  function populateLeadDropdown() {
    var dd = document.getElementById('cp-country-dropdown');
    if (!dd || dd.dataset.populated === 'true') return;
    dd.innerHTML = '';
    COUNTRIES.forEach(function(country) {
      var item = document.createElement('button');
      item.type = 'button';
      item.className = 'w-full flex items-center gap-2 px-3 py-2 text-sm text-white hover:bg-white/10 text-left';
      item.dataset.code = country.code;
      item.innerHTML = flagImg(country.code) + '<span class="flex-1 truncate">' + country.name + '</span><span class="text-gray-400">' + country.dial + '</span>';
      dd.appendChild(item);
    });
    dd.dataset.populated = 'true';
  }

  // Event delegation for ALL country picker clicks (lead modal)
  document.addEventListener('click', function(e) {
    var leadBtn = e.target.closest('#cp-country-btn');
    if (leadBtn) {
      e.preventDefault();
      e.stopPropagation();
      populateLeadDropdown();
      var dd = document.getElementById('cp-country-dropdown');
      if (dd) dd.style.display = (dd.style.display === 'none' || !dd.style.display) ? 'block' : 'none';
      return;
    }
    var inLeadDd = e.target.closest('#cp-country-dropdown button');
    if (inLeadDd) {
      e.preventDefault();
      e.stopPropagation();
      var code = inLeadDd.dataset.code;
      var country = findCountry(code);
      if (country) {
        applyCountryTo('cp-country-flag', 'cp-country-code', country);
        applyCountryTo('demo-country-flag', 'demo-country-code', country);
        window.demoSelectedDial = country.dial;
      }
      var dd = document.getElementById('cp-country-dropdown');
      if (dd) dd.style.display = 'none';
      return;
    }
    if (!e.target.closest('#cp-country-dropdown') && !e.target.closest('#cp-country-btn')) {
      var dd = document.getElementById('cp-country-dropdown');
      if (dd) dd.style.display = 'none';
    }
  }, true);

  function detectCountry() {
    var fallback = findCountry('BR');
    if (fallback) applyDefault(fallback);

    var langs = (navigator.languages && navigator.languages.length) ? navigator.languages : [navigator.language || navigator.userLanguage || ''];
    for (var i = 0; i < langs.length; i++) {
      var lang = (langs[i] || '').toLowerCase();
      var code = LANG_TO_COUNTRY[lang] || LANG_TO_COUNTRY[lang.split('-')[0]];
      if (code) {
        var m = findCountry(code);
        if (m) { applyDefault(m); return; }
      }
    }

    fetch('https://api.country.is/', {cache:'no-store'})
      .then(function(r){ return r.ok ? r.json() : null; })
      .then(function(data){
        if (!data || !data.country) return;
        var m = findCountry(data.country);
        if (m) applyDefault(m);
      })
      .catch(function(){});
  }

  populateLeadDropdown();
  detectCountry();
})();
</script>
"""

body_end = c.rfind('</body>')
c = c[:body_end] + NEW_SCRIPT + c[body_end:]
p.write_text(c, encoding='utf-8')
print(f'new script injected ({len(NEW_SCRIPT)} chars)')
print(f'file size: {len(c)}')
