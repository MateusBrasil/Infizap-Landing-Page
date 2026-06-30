# -*- coding: utf-8 -*-
"""Procura no universal-script de t.infizap.com qualquer init/load de
pixel proprio que nao seja so disparo de evento."""
import io, os, re, base64

PATH = os.path.join(os.path.dirname(__file__), "infizap-lp-v1.html")

with io.open(PATH, "r", encoding="utf-8") as f:
    html = f.read()

# Extrai o conteudo do universal-script.
m = re.search(
    r'"https://t\.infizap\.com/v1/lst/universal-script[^"]*":"data:[^,]+,([A-Za-z0-9+/=]+)"',
    html,
)
content = base64.b64decode(m.group(1)).decode("utf-8", errors="replace")
print(f"Tamanho: {len(content):,} bytes\n")

# Padroes de init de pixel
SEARCH = [
    (r"fbq\([^)]{0,200}\)", "Toda chamada fbq()"),
    (r"_fbq", "Refs a _fbq"),
    (r"window\.fbq", "window.fbq"),
    (r"pixelId|pixel_id|pixel ID", "Vars de pixelId"),
    (r"fbevents", "fbevents"),
    (r"connect\.facebook", "Domain facebook"),
    (r"\b\d{15,16}\b", "Numeros de 15-16 digitos (pixel IDs)"),
]
for pat, label in SEARCH:
    hits = re.findall(pat, content)
    print(f"=== {label} ({pat}): {len(hits)} hits ===")
    seen = set()
    for h in hits[:20]:
        if h not in seen:
            seen.add(h)
            print(f"  - {h}")
    print()
