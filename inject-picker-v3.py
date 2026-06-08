"""V3: IP-first detection, force re-populate, 85 countries, robust event delegation."""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

p = Path('infizap-lp-v1.html')
c = p.read_text(encoding='utf-8')

# 85 countries — Portuguese names, alphabetical, valid ISO + dial
COUNTRIES = [
    ('ZA','+27','África do Sul'),       ('AL','+355','Albânia'),
    ('DE','+49','Alemanha'),            ('AD','+376','Andorra'),
    ('AO','+244','Angola'),             ('SA','+966','Arábia Saudita'),
    ('AR','+54','Argentina'),           ('AU','+61','Austrália'),
    ('AT','+43','Áustria'),             ('AZ','+994','Azerbaijão'),
    ('BH','+973','Bahrein'),            ('BD','+880','Bangladesh'),
    ('BY','+375','Belarus'),            ('BE','+32','Bélgica'),
    ('BO','+591','Bolívia'),            ('BA','+387','Bósnia'),
    ('BR','+55','Brasil'),              ('BG','+359','Bulgária'),
    ('CA','+1','Canadá'),               ('QA','+974','Catar'),
    ('KZ','+7','Cazaquistão'),          ('CL','+56','Chile'),
    ('CN','+86','China'),               ('CY','+357','Chipre'),
    ('CO','+57','Colômbia'),            ('KR','+82','Coreia do Sul'),
    ('CI','+225','Costa do Marfim'),    ('CR','+506','Costa Rica'),
    ('HR','+385','Croácia'),            ('CU','+53','Cuba'),
    ('DK','+45','Dinamarca'),           ('EG','+20','Egito'),
    ('SV','+503','El Salvador'),        ('AE','+971','Emirados Árabes'),
    ('EC','+593','Equador'),            ('SK','+421','Eslováquia'),
    ('SI','+386','Eslovênia'),          ('ES','+34','Espanha'),
    ('US','+1','Estados Unidos'),       ('EE','+372','Estônia'),
    ('PH','+63','Filipinas'),           ('FI','+358','Finlândia'),
    ('FR','+33','França'),              ('GH','+233','Gana'),
    ('GR','+30','Grécia'),              ('GT','+502','Guatemala'),
    ('HK','+852','Hong Kong'),          ('NL','+31','Holanda'),
    ('HN','+504','Honduras'),           ('HU','+36','Hungria'),
    ('YE','+967','Iêmen'),              ('IN','+91','Índia'),
    ('ID','+62','Indonésia'),           ('IQ','+964','Iraque'),
    ('IR','+98','Irã'),                 ('IE','+353','Irlanda'),
    ('IS','+354','Islândia'),           ('IL','+972','Israel'),
    ('IT','+39','Itália'),              ('JM','+1876','Jamaica'),
    ('JP','+81','Japão'),               ('JO','+962','Jordânia'),
    ('KW','+965','Kuwait'),             ('LV','+371','Letônia'),
    ('LB','+961','Líbano'),             ('LT','+370','Lituânia'),
    ('LU','+352','Luxemburgo'),         ('MY','+60','Malásia'),
    ('MT','+356','Malta'),              ('MA','+212','Marrocos'),
    ('MX','+52','México'),              ('MZ','+258','Moçambique'),
    ('NG','+234','Nigéria'),            ('NI','+505','Nicarágua'),
    ('NO','+47','Noruega'),             ('NZ','+64','Nova Zelândia'),
    ('OM','+968','Omã'),                ('PK','+92','Paquistão'),
    ('PA','+507','Panamá'),             ('PY','+595','Paraguai'),
    ('PE','+51','Peru'),                ('PL','+48','Polônia'),
    ('PT','+351','Portugal'),           ('KE','+254','Quênia'),
    ('GB','+44','Reino Unido'),         ('DO','+1809','República Dominicana'),
    ('CZ','+420','República Tcheca'),   ('RO','+40','Romênia'),
    ('RU','+7','Rússia'),               ('SG','+65','Singapura'),
    ('SY','+963','Síria'),              ('LK','+94','Sri Lanka'),
    ('SE','+46','Suécia'),              ('CH','+41','Suíça'),
    ('TH','+66','Tailândia'),           ('TW','+886','Taiwan'),
    ('TZ','+255','Tanzânia'),           ('TN','+216','Tunísia'),
    ('TR','+90','Turquia'),             ('UA','+380','Ucrânia'),
    ('UG','+256','Uganda'),             ('UY','+598','Uruguai'),
    ('VE','+58','Venezuela'),           ('VN','+84','Vietnã'),
]

js_arr = '[' + ','.join(
    "{c:'%s',d:'%s',n:'%s'}" % (code, dial, name)
    for code, dial, name in COUNTRIES
) + ']'

NEW_SCRIPT = """
<script>
(function(){
  var L = """ + js_arr + """;

  function find(code){ code=(code||'').toUpperCase(); for(var i=0;i<L.length;i++) if(L[i].c===code) return L[i]; return null; }
  function flag(code){ return '<img src="https://flagcdn.com/w40/'+code.toLowerCase()+'.png" alt="" width="20" height="14" class="rounded-sm shrink-0" style="object-fit:cover;display:inline-block;vertical-align:middle">'; }

  function apply(country){
    var spec = [
      ['cp-country-flag','cp-country-code'],
      ['demo-country-flag','demo-country-code']
    ];
    spec.forEach(function(pair){
      var fe = document.getElementById(pair[0]);
      var ce = document.getElementById(pair[1]);
      if (fe) fe.innerHTML = flag(country.c);
      if (ce) ce.textContent = country.d;
    });
    window.demoSelectedDial = country.d;
  }

  function buildItem(country){
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'w-full flex items-center gap-2 px-3 py-2 text-sm text-white hover:bg-white/10 text-left';
    btn.dataset.code = country.c;
    btn.innerHTML = flag(country.c)+'<span class="flex-1 truncate">'+country.n+'</span><span class="text-gray-400 shrink-0">'+country.d+'</span>';
    return btn;
  }

  // Force re-populate every time (no caching guard — defends against any leftover content)
  function populate(ddId){
    var dd = document.getElementById(ddId);
    if (!dd) return;
    // Aggressive clear — remove ALL children to wipe any leftover static markup
    while (dd.firstChild) dd.removeChild(dd.firstChild);
    L.forEach(function(country){ dd.appendChild(buildItem(country)); });
  }

  function populateAll(){
    populate('cp-country-dropdown');
    populate('demo-country-dropdown');
  }

  // Single global click handler covers ALL pickers — works whenever modal mounts
  document.addEventListener('click', function(e){
    var leadBtn = e.target.closest('#cp-country-btn');
    var demoBtn = e.target.closest('#demo-country-btn');
    var insideLeadDd = e.target.closest('#cp-country-dropdown');
    var insideDemoDd = e.target.closest('#demo-country-dropdown');

    if (leadBtn){
      e.preventDefault(); e.stopPropagation();
      populate('cp-country-dropdown');  // re-populate every open
      var dd = document.getElementById('cp-country-dropdown');
      if (dd) dd.style.display = (dd.style.display==='none'||!dd.style.display)?'block':'none';
      // Close demo dropdown if open
      var ddd = document.getElementById('demo-country-dropdown'); if (ddd) ddd.style.display = 'none';
      return;
    }
    if (demoBtn){
      e.preventDefault(); e.stopPropagation();
      populate('demo-country-dropdown');
      var dd = document.getElementById('demo-country-dropdown');
      if (dd) dd.style.display = (dd.style.display==='none'||!dd.style.display)?'block':'none';
      var ldd = document.getElementById('cp-country-dropdown'); if (ldd) ldd.style.display = 'none';
      return;
    }

    var clickedItem = e.target.closest('#cp-country-dropdown button, #demo-country-dropdown button');
    if (clickedItem){
      e.preventDefault(); e.stopPropagation();
      var country = find(clickedItem.dataset.code);
      if (country) apply(country);
      var d1 = document.getElementById('cp-country-dropdown'); if (d1) d1.style.display = 'none';
      var d2 = document.getElementById('demo-country-dropdown'); if (d2) d2.style.display = 'none';
      return;
    }

    // Outside click — close both
    if (!insideLeadDd && !insideDemoDd){
      var d1 = document.getElementById('cp-country-dropdown'); if (d1) d1.style.display = 'none';
      var d2 = document.getElementById('demo-country-dropdown'); if (d2) d2.style.display = 'none';
    }
  }, true);

  // Detection chain — IP first (true location), language as fallback, BR as last resort
  function detect(){
    var langMap = {
      'pt-br':'BR','pt-pt':'PT','pt':'BR',
      'es-mx':'MX','es-ar':'AR','es-co':'CO','es-cl':'CL','es-pe':'PE','es-ec':'EC',
      'es-ve':'VE','es-uy':'UY','es-py':'PY','es-bo':'BO','es-cu':'CU','es-do':'DO',
      'es-gt':'GT','es-hn':'HN','es-sv':'SV','es-ni':'NI','es-cr':'CR','es-pa':'PA','es':'ES',
      'en-gb':'GB','en-ca':'CA','en-au':'AU','en-nz':'NZ','en-ie':'IE','en-za':'ZA','en':'US',
      'fr-ca':'CA','fr-be':'BE','fr-ch':'CH','fr':'FR',
      'de-at':'AT','de-ch':'CH','de':'DE','it':'IT',
      'nl-be':'BE','nl':'NL','sv':'SE','da':'DK','no':'NO','nb':'NO','fi':'FI',
      'pl':'PL','cs':'CZ','sk':'SK','hu':'HU','ro':'RO','bg':'BG',
      'el':'GR','tr':'TR','uk':'UA','ru':'RU','he':'IL',
      'ar-ae':'AE','ar-eg':'EG','ar-ma':'MA','ar':'SA',
      'ja':'JP','ko':'KR','zh-tw':'TW','zh':'CN',
      'th':'TH','vi':'VN','id':'ID','ms':'MY','hi':'IN'
    };

    function fromLang(){
      var langs = (navigator.languages && navigator.languages.length) ? navigator.languages : [navigator.language||navigator.userLanguage||''];
      for (var i=0;i<langs.length;i++){
        var lang = (langs[i]||'').toLowerCase();
        var code = langMap[lang] || langMap[lang.split('-')[0]];
        if (code){ var m=find(code); if (m) return m; }
      }
      return null;
    }

    // Try IP geo services in order; first to succeed wins
    var services = [
      { url:'https://ipapi.co/json/',     key:'country_code' },
      { url:'https://api.country.is/',    key:'country' },
      { url:'https://ipwhois.app/json/',  key:'country_code' }
    ];

    var done = false;
    function applyIfLive(country){
      if (done || !country) return;
      done = true;
      apply(country);
    }

    services.forEach(function(svc){
      fetch(svc.url, {cache:'no-store'})
        .then(function(r){ return r.ok ? r.json() : null; })
        .then(function(data){
          if (done || !data) return;
          var cc = data[svc.key];
          if (!cc) return;
          var m = find(cc);
          if (m) applyIfLive(m);
        })
        .catch(function(){});
    });

    // If IP services don't reply in 2s, fall back to language guess
    setTimeout(function(){
      if (done) return;
      var lang = fromLang();
      if (lang) applyIfLive(lang);
      else { var br=find('BR'); if (br) applyIfLive(br); }
    }, 2000);

    // Final safety: 5s timeout BR
    setTimeout(function(){
      if (done) return;
      var br = find('BR'); if (br) applyIfLive(br);
    }, 5000);
  }

  // Init
  populateAll();
  detect();
})();
</script>
"""

body_end = c.rfind('</body>')
c = c[:body_end] + NEW_SCRIPT + c[body_end:]
p.write_text(c, encoding='utf-8')
print(f'v3 injected, file size: {len(c)}')
print(f'countries: {len(COUNTRIES)}')
