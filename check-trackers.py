# -*- coding: utf-8 -*-
"""Decodifica os scripts interceptados pelo Umbrella mirror e procura
qualquer referencia a pixel da Meta (407..., fbq, fbevents)."""
import io, os, re, base64

PATH = os.path.join(os.path.dirname(__file__), "infizap-lp-v1.html")
TARGETS = [
    "https://team.infizap.com/js/external-tracking.js",
    "https://t.infizap.com/v1/lst/universal-script",
    "https://www.googletagmanager.com/gtm.js?id=GTM-T54P7M6Q",
]
SUSPECT_PATTERNS = [
    r"407533577279582",
    r"fbq\(",
    r"fbevents\.js",
    r"facebook\.com/tr",
]

with io.open(PATH, "r", encoding="utf-8") as f:
    html = f.read()

# Procura entradas do MAP: "URL":"data:application/javascript;base64,XXXX"
# As URLs podem aparecer com escapes JS (\/), entao normalizamos.
for url in TARGETS:
    print(f"\n=== {url} ===")
    # Tentamos achar tanto URL puro quanto URL com query escapada
    # O MAP nao escapa as URLs porque a chave e literal.
    # Vamos buscar "URL_PREFIX que comeca o data: URI logo apos
    # Tentativa 1: match exato
    found = False
    for variant in [url, url.replace("?", "\\?")]:
        m = re.search(re.escape(url.split("?")[0]) + r'[^"]*":"data:[^,]+,([A-Za-z0-9+/=]+)"', html)
        if m:
            b64 = m.group(1)
            try:
                content = base64.b64decode(b64).decode("utf-8", errors="replace")
            except Exception as e:
                print(f"  [erro decodificando: {e}]")
                continue
            print(f"  Tamanho: {len(content):,} bytes")
            for pat in SUSPECT_PATTERNS:
                hits = re.findall(pat, content)
                if hits:
                    print(f"  PADRAO '{pat}': {len(hits)} hits")
                    # mostra contexto da primeira
                    mm = re.search(pat, content)
                    if mm:
                        start = max(0, mm.start() - 80)
                        end = min(len(content), mm.end() + 120)
                        snippet = content[start:end].replace("\n", "\\n")
                        print(f"    contexto: ...{snippet}...")
            found = True
            break
    if not found:
        print("  [nao encontrado no MAP do interceptor]")
