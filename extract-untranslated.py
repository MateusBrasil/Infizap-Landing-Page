"""Extract all visible PT text nodes from HTML not yet in en.json."""
import sys, re, json
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

en = json.loads(Path('i18n/en.json').read_text(encoding='utf-8'))
en_keys = set(en.keys())

html = Path('infizap-lp-v1.html').read_text(encoding='utf-8')

# Strip all <script>, <style>, <noscript> blocks
html2 = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
html2 = re.sub(r'<style\b[^>]*>.*?</style>', '', html2, flags=re.DOTALL|re.IGNORECASE)
html2 = re.sub(r'<noscript\b[^>]*>.*?</noscript>', '', html2, flags=re.DOTALL|re.IGNORECASE)
html2 = re.sub(r'<!--.*?-->', '', html2, flags=re.DOTALL)

# Find all text between > and < (i.e., text content)
texts = re.findall(r'>([^<>]+)<', html2)

# Filter for "translatable" strings: contains a letter, length 2-200, has Portuguese characters or words
seen = set()
candidates = []
PT_WORDS = re.compile(r'\b(de|da|do|para|por|com|sem|sua|seu|seus|suas|nas|nos|num|você|que|não|este|esta|isso|quando|onde|porquê|sim|você|veja|começ|tudo|operação|tempo|atendimento|dados|painel|equipe|cliente|empresa|negócio|venda|venda|compr|trabalh|funciona|primeiro|últim|melhor|maior|gerar|usar|ver|fazer|deix|deix|pra|tem|temos|ter|aqui|ali|isso|isso|nosso|todos|todas|você|sobre|junto|onde|porque|quer|deixe|deixar|nada|todo|toda|também|sempre|nunca|grátis|pagar|preço|hora|hoje|amanhã|ontem|cada|outro|outra|mesmo|próprio|mesm|mesm|antes|depois|durante|sobre)\b', re.IGNORECASE)
HAS_LETTER = re.compile(r'[a-zA-ZáéíóúâêîôûãõçÁÉÍÓÚÂÊÎÔÛÃÕÇ]')

for raw in texts:
    s = raw.strip()
    if not s or len(s) < 2 or len(s) > 400:
        continue
    if not HAS_LETTER.search(s):
        continue
    # Skip already-translated
    if s in en_keys:
        continue
    if s in seen:
        continue
    seen.add(s)
    # Skip pure-symbol / pure-number lines
    if not re.search(r'[a-záéíóúâêîôûãõç]', s, re.IGNORECASE):
        continue
    # Skip stuff that's clearly URL/email/symbol noise
    if s.startswith('http') or '@' in s and len(s) < 40 and ' ' not in s:
        continue
    # Skip already-translated entries
    candidates.append(s)

# Sort by length desc to prefer longer matches first
candidates.sort(key=lambda x: (-len(x), x))

print(f'Found {len(candidates)} candidates not yet in en.json')
print('---FULL LIST (truncated to 600 first chars per)---')
for c in candidates[:300]:
    snippet = c if len(c) <= 200 else c[:200] + '...'
    print(repr(snippet))
