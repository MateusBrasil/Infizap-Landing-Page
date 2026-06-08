"""
Aplica:
1. Tradução das labels/placeholders Espanhol -> Português nos modais
2. Substitui DEMO_COUNTRIES com lista correta (60+ países, PT, alfabética)
3. Modifica populateDemoCountryDropdown pra renderizar com SVG (flagcdn.com)
4. Substitui buttons estáticos do lead modal por placeholder vazio
5. Injeta novo <script> que: gerencia o picker do lead modal, faz IP geolocation,
   e pre-seleciona o país nos 2 modais
"""
import sys, re
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

p = Path('infizap-lp-v1.html')
c = p.read_text(encoding='utf-8')

# =============================================================================
# PHASE 1 — Traduções Espanhol -> Português
# =============================================================================
TRANSLATIONS = [
    ('>Nombre</label>', '>Nome</label>'),
    ('placeholder="Tu nombre completo"', 'placeholder="Seu nome completo"'),
    ('placeholder="Ingresa tu nombre"', 'placeholder="Digite seu nome"'),
    ('>Teléfono</label>', '>Telefone</label>'),
    ('>Correo</label>', '>E-mail</label>'),
    ('placeholder="tu@correo.com"', 'placeholder="voce@email.com"'),
    ('placeholder="Ingresa tu correo principal"', 'placeholder="Digite seu e-mail principal"'),
    ('placeholder="Ingresa tu número de WhatsApp"', 'placeholder="Digite seu número de WhatsApp"'),
    ('aria-label="Cerrar"', 'aria-label="Fechar"'),
    ('>Cerrar</span>', '>Fechar</span>'),
    ("'Por favor completa todos los campos.'", "'Por favor preencha todos os campos.'"),
    ("'Por favor confirma que entiendes el propósito de la sesión.'", "'Por favor confirme que entendeu o propósito da sessão.'"),
]
trans_count = 0
for old, new in TRANSLATIONS:
    n = c.count(old)
    if n:
        c = c.replace(old, new)
        trans_count += n
        print(f'  translated: "{old[:50]}..." ({n}x)')
print(f'Total translations: {trans_count}\n')

# =============================================================================
# PHASE 2 — Substituir DEMO_COUNTRIES com lista correta
# =============================================================================
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
    ('FR','+33','França'),              ('GR','+30','Grécia'),
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
print(f'Total countries: {len(COUNTRIES)}\n')

# Build JS array literal
js_arr = '[\n' + ',\n'.join(
    f"    {{code:'{code}',dial:'{dial}',name:'{name}'}}"
    for code, dial, name in COUNTRIES
) + '\n  ]'

# Find DEMO_COUNTRIES = [...] and replace
arr_match = re.search(r'(var\s+DEMO_COUNTRIES\s*=\s*)\[.*?\];', c, re.DOTALL)
if arr_match:
    new_decl = arr_match.group(1) + js_arr + ';'
    c = c[:arr_match.start()] + new_decl + c[arr_match.end():]
    print(f'DEMO_COUNTRIES array replaced ({len(arr_match.group(0))} -> {len(new_decl)} chars)')
else:
    print('ERROR: DEMO_COUNTRIES declaration not found')
    sys.exit(1)

# =============================================================================
# PHASE 3 — Modificar populateDemoCountryDropdown para usar SVG (img flagcdn)
#           e o click handler para setar flag como <img>
# =============================================================================

# Locate the populateDemoCountryDropdown function body
fn_match = re.search(
    r'function\s+populateDemoCountryDropdown\(\)\s*\{[^}]*?DEMO_COUNTRIES\.forEach[^}]*?\}\s*\)\s*;\s*\}',
    c, re.DOTALL
)
if not fn_match:
    # Fallback: find by substring and walk braces
    p_start = c.find('function populateDemoCountryDropdown')
    if p_start < 0:
        print('ERROR: populateDemoCountryDropdown not found'); sys.exit(1)
    # Walk braces from first {
    body_start = c.find('{', p_start)
    depth = 1; pos = body_start + 1
    while depth > 0 and pos < len(c):
        ch = c[pos]
        if ch == '{': depth += 1
        elif ch == '}': depth -= 1
        pos += 1
    fn_end = pos
    old_fn = c[p_start:fn_end]
    print(f'Function span (brace walk): {p_start}..{fn_end} ({fn_end-p_start} chars)')
else:
    p_start = fn_match.start()
    fn_end = fn_match.end()
    old_fn = c[p_start:fn_end]
    print(f'Function span (regex): {p_start}..{fn_end} ({fn_end-p_start} chars)')

new_fn = """function populateDemoCountryDropdown() {
    var dd = document.getElementById('demo-country-dropdown');
    if (!dd) return;
    dd.innerHTML = '';
    DEMO_COUNTRIES.forEach(function(c) {
      var item = document.createElement('button');
      item.type = 'button';
      item.className = 'w-full flex items-center gap-2 px-3 py-2 text-sm text-white hover:bg-white/10 text-left';
      var flagSrc = 'https://flagcdn.com/w40/' + c.code.toLowerCase() + '.png';
      item.innerHTML = '<img src="' + flagSrc + '" alt="" width="20" height="14" class="shrink-0 rounded-sm" style="object-fit:cover"><span class="flex-1 truncate">' + c.name + '</span><span class="text-gray-400">' + c.dial + '</span>';
      item.addEventListener('click', function() {
        demoSelectedDial = c.dial;
        var flagEl = document.getElementById('demo-country-flag');
        var codeEl = document.getElementById('demo-country-code');
        if (flagEl) flagEl.innerHTML = '<img src="' + flagSrc + '" alt="" width="20" height="14" class="rounded-sm" style="object-fit:cover">';
        if (codeEl) codeEl.textContent = c.dial;
        dd.style.display = 'none';
      });
      dd.appendChild(item);
    });
  }"""

c = c[:p_start] + new_fn + c[fn_end:]
print(f'populateDemoCountryDropdown replaced')

# =============================================================================
# PHASE 4 — Aumentar largura do dropdown (era w-[200px], precisa de mais espaço para nomes longos)
# =============================================================================
old_w = 'id="demo-country-dropdown" style="display:none" class="absolute top-full left-0 mt-1 w-[200px] max-h-[240px]'
new_w = 'id="demo-country-dropdown" style="display:none" class="absolute top-full left-0 mt-1 w-[260px] max-h-[280px]'
if old_w in c:
    c = c.replace(old_w, new_w)
    print('demo dropdown width expanded to 260px')

old_w_lead = 'id="cp-country-dropdown" style="display:none" class="absolute top-full left-0 mt-1 w-[200px] max-h-[240px]'
new_w_lead = 'id="cp-country-dropdown" style="display:none" class="absolute top-full left-0 mt-1 w-[260px] max-h-[280px]'
if old_w_lead in c:
    c = c.replace(old_w_lead, new_w_lead)
    print('lead dropdown width expanded to 260px')

# =============================================================================
# PHASE 5 — Substituir buttons estáticos do lead modal com dropdown vazio
# =============================================================================
# Find the start of cp-country-dropdown and the end (closing </div>)
ds = c.find('id="cp-country-dropdown"')
# Find the opening <div ... >
div_open_end = c.find('>', ds) + 1
# Find the matching </div> - walk braces / tag depth
depth = 1
pos = div_open_end
while depth > 0:
    no = c.find('<div', pos)
    nc = c.find('</div>', pos)
    nb = c.find('<button', pos)
    # Use simple counter: any open tag increments, any close decrements
    # For HTML, we count <div and </div only since buttons don't nest divs here
    if no == -1 or nc < no:
        depth -= 1
        pos = nc + 6
    else:
        depth += 1
        pos = no + 4
# Replace inner content with empty (will be populated by JS)
old_dropdown = c[div_open_end:pos-6]  # content between <div...> and </div>
new_dropdown_content = ''  # empty; will be filled by JS
c = c[:div_open_end] + new_dropdown_content + c[pos-6:]
print(f'lead dropdown content cleared ({len(old_dropdown)} chars removed)')

# =============================================================================
# PHASE 6 — Substituir os emojis nos botões flag por placeholder vazio (será preenchido por JS)
# =============================================================================
# Initial flag in cp-country-flag and demo-country-flag (both show 🇨🇴)
# Replace with empty span - JS will fill in based on IP
old_cp_flag = '<span id="cp-country-flag" data-astro-cid-7jt2x4ie="">🇨🇴</span>'
new_cp_flag = '<span id="cp-country-flag" data-astro-cid-7jt2x4ie=""></span>'
if old_cp_flag in c:
    c = c.replace(old_cp_flag, new_cp_flag)
    print('cp-country-flag emoji cleared')

old_demo_flag = '<span id="demo-country-flag">🇨🇴</span>'
new_demo_flag = '<span id="demo-country-flag"></span>'
if old_demo_flag in c:
    c = c.replace(old_demo_flag, new_demo_flag)
    print('demo-country-flag emoji cleared')

# Also clear the dial code from defaults — will be set by JS
old_cp_code = '<span id="cp-country-code" class="text-gray-400" data-astro-cid-7jt2x4ie="">+57</span>'
new_cp_code = '<span id="cp-country-code" class="text-gray-400" data-astro-cid-7jt2x4ie="">+55</span>'
if old_cp_code in c:
    c = c.replace(old_cp_code, new_cp_code)
    print('cp-country-code default to +55')

old_demo_code = '<span id="demo-country-code" class="text-gray-400">+57</span>'
new_demo_code = '<span id="demo-country-code" class="text-gray-400">+55</span>'
if old_demo_code in c:
    c = c.replace(old_demo_code, new_demo_code)
    print('demo-country-code default to +55')

# =============================================================================
# PHASE 7 — Adicionar script de unificação (lead modal picker + IP detection)
# =============================================================================
NEW_SCRIPT = """
<script>
(function(){
  // Países (mesma lista do demo, espelhada aqui pra independência)
  var INFIZAP_COUNTRIES = """ + js_arr + """;

  function flagImg(code) {
    var src = 'https://flagcdn.com/w40/' + code.toLowerCase() + '.png';
    return '<img src="' + src + '" alt="" width="20" height="14" class="rounded-sm" style="object-fit:cover">';
  }

  // Apply selected country to a modal's flag/code spans
  function applyCountryTo(flagId, codeId, country) {
    var fe = document.getElementById(flagId);
    var ce = document.getElementById(codeId);
    if (fe) fe.innerHTML = flagImg(country.code);
    if (ce) ce.textContent = country.dial;
  }

  // Populate lead modal dropdown (cp-country-dropdown)
  function populateLeadDropdown() {
    var dd = document.getElementById('cp-country-dropdown');
    if (!dd) return;
    dd.innerHTML = '';
    INFIZAP_COUNTRIES.forEach(function(country) {
      var item = document.createElement('button');
      item.type = 'button';
      item.className = 'w-full flex items-center gap-2 px-3 py-2 text-sm text-white hover:bg-white/10 text-left';
      item.innerHTML = flagImg(country.code) + '<span class="flex-1 truncate">' + country.name + '</span><span class="text-gray-400">' + country.dial + '</span>';
      item.addEventListener('click', function(e) {
        e.stopPropagation();
        applyCountryTo('cp-country-flag', 'cp-country-code', country);
        dd.style.display = 'none';
      });
      dd.appendChild(item);
    });
  }

  // Lead modal: open/close dropdown
  function wireLeadPicker() {
    var btn = document.getElementById('cp-country-btn');
    var dd = document.getElementById('cp-country-dropdown');
    if (btn && dd) {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        dd.style.display = dd.style.display === 'none' ? 'block' : 'none';
      });
      document.addEventListener('click', function() {
        dd.style.display = 'none';
      });
    }
  }

  // Apply default country (Brasil) to both modals
  function applyDefault(country) {
    applyCountryTo('cp-country-flag', 'cp-country-code', country);
    applyCountryTo('demo-country-flag', 'demo-country-code', country);
    // Also update demoSelectedDial used by the demo modal handler
    if (typeof window.demoSelectedDial !== 'undefined') {
      window.demoSelectedDial = country.dial;
    }
  }

  function findCountry(code) {
    code = (code || '').toUpperCase();
    for (var i = 0; i < INFIZAP_COUNTRIES.length; i++) {
      if (INFIZAP_COUNTRIES[i].code === code) return INFIZAP_COUNTRIES[i];
    }
    return null;
  }

  // IP geolocation via api.country.is (free, no key)
  function detectCountry() {
    var DEFAULT = findCountry('BR');
    if (DEFAULT) applyDefault(DEFAULT);
    fetch('https://api.country.is/', { method: 'GET' })
      .then(function(r) { return r.ok ? r.json() : null; })
      .then(function(data) {
        if (!data || !data.country) return;
        var match = findCountry(data.country);
        if (match) applyDefault(match);
      })
      .catch(function(){ /* silent: keep BR default */ });
  }

  // Init when DOM ready
  function init() {
    populateLeadDropdown();
    wireLeadPicker();
    detectCountry();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
</script>
"""

# Insert just before </body>
body_end = c.rfind('</body>')
if body_end < 0:
    print('ERROR: </body> not found')
    sys.exit(1)
c = c[:body_end] + NEW_SCRIPT + c[body_end:]
print(f'unified picker/IP script injected ({len(NEW_SCRIPT)} chars)')

p.write_text(c, encoding='utf-8')
print(f'\nFile size: {len(c)}')
