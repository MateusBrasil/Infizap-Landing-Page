"""
Rebuild integrations marquee: substitui logos antigos (Brevo, Stripe, HubSpot,
GoHighLevel, Zapier, Make, Mailerlite, GetResponse, ActiveCampaign, MailChimp,
Calendly, Slack, Notion, Hotmart) pelos 10 que o cliente pediu:

  WhatsApp Oficial, Instagram, Facebook Messenger, OpenAI/ChatGPT,
  Google Gemini, Dialogflow, Typebot, n8n, Webhooks, Cal.com

Todos os logos em SVG branco monocromático (24x24 viewBox).
"""
import re, sys, base64
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

# ===== SVG LOGOS (branco monocromático) =====
# 32x32 px com fill branco — estilo limpo, padrão de mercado.

LOGOS = {
    # 1. WhatsApp (oficial, balão com fone)
    'WhatsApp': '''<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none"><path fill="#fff" d="M16 3C8.82 3 3 8.82 3 16c0 2.29.6 4.43 1.65 6.3L3 29l6.85-1.8A12.97 12.97 0 0 0 16 29c7.18 0 13-5.82 13-13S23.18 3 16 3Zm0 23.6c-1.97 0-3.84-.52-5.45-1.5l-.39-.23-4.07 1.07 1.09-3.97-.25-.41A10.5 10.5 0 0 1 5.4 16C5.4 10.16 10.16 5.4 16 5.4S26.6 10.16 26.6 16 21.84 26.6 16 26.6Zm5.78-7.92c-.32-.16-1.88-.93-2.17-1.04-.29-.1-.5-.16-.71.16-.21.32-.81 1.04-1 1.25-.18.21-.37.24-.69.08-.32-.16-1.34-.49-2.55-1.57-.94-.84-1.58-1.88-1.77-2.2-.18-.32-.02-.49.14-.65.14-.14.32-.37.48-.55.16-.18.21-.32.32-.53.1-.21.05-.4-.03-.55-.08-.16-.71-1.7-.97-2.33-.26-.62-.52-.53-.71-.54-.18-.01-.4-.01-.61-.01-.21 0-.55.08-.84.4-.29.32-1.1 1.08-1.1 2.63s1.13 3.05 1.29 3.26c.16.21 2.22 3.39 5.39 4.75.75.33 1.34.52 1.8.67.76.24 1.45.21 1.99.13.61-.09 1.88-.77 2.14-1.51.26-.74.26-1.37.18-1.51-.08-.13-.29-.21-.61-.37Z"/></svg>''',

    # 2. Instagram (câmera quadrada com círculo)
    'Instagram': '''<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none"><path fill="#fff" d="M16 5.6c3.39 0 3.79.02 5.13.08 1.24.06 1.91.26 2.36.44.59.23 1.02.5 1.46.95.45.45.72.87.95 1.46.18.45.38 1.12.44 2.36.06 1.34.08 1.74.08 5.13 0 3.39-.02 3.79-.08 5.13-.06 1.24-.26 1.91-.44 2.36-.23.59-.5 1.02-.95 1.46-.45.45-.87.72-1.46.95-.45.18-1.12.38-2.36.44-1.34.06-1.74.08-5.13.08-3.39 0-3.79-.02-5.13-.08-1.24-.06-1.91-.26-2.36-.44-.59-.23-1.02-.5-1.46-.95-.45-.45-.72-.87-.95-1.46-.18-.45-.38-1.12-.44-2.36-.06-1.34-.08-1.74-.08-5.13 0-3.39.02-3.79.08-5.13.06-1.24.26-1.91.44-2.36.23-.59.5-1.02.95-1.46.45-.45.87-.72 1.46-.95.45-.18 1.12-.38 2.36-.44 1.34-.06 1.74-.08 5.13-.08M16 3c-3.45 0-3.88.01-5.24.08-1.35.06-2.27.27-3.08.59-.83.32-1.54.76-2.24 1.46S4.4 6.65 4.07 7.48c-.31.81-.53 1.74-.59 3.08C3.41 11.92 3.4 12.35 3.4 16s.01 4.08.08 5.44c.06 1.35.27 2.27.59 3.08.32.83.76 1.54 1.46 2.24s1.41 1.13 2.24 1.46c.81.31 1.74.53 3.08.59C12.12 28.83 12.55 28.85 16 28.85s4.08-.02 5.44-.08c1.35-.06 2.27-.27 3.08-.59.83-.32 1.54-.76 2.24-1.46s1.13-1.41 1.46-2.24c.31-.81.53-1.74.59-3.08.06-1.36.08-1.79.08-5.44s-.01-4.08-.08-5.44c-.06-1.35-.27-2.27-.59-3.08-.32-.83-.76-1.54-1.46-2.24S25.35 4.4 24.52 4.07c-.81-.31-1.74-.53-3.08-.59C19.88 3.41 19.45 3.4 16 3.4Z"/><path fill="#fff" d="M16 9.32A6.68 6.68 0 1 0 22.68 16 6.68 6.68 0 0 0 16 9.32Zm0 11.02A4.34 4.34 0 1 1 20.34 16 4.34 4.34 0 0 1 16 20.34ZM22.95 7.49a1.56 1.56 0 1 0 1.56 1.56 1.56 1.56 0 0 0-1.56-1.56Z"/></svg>''',

    # 3. Facebook Messenger (raio dentro de balão)
    'Messenger': '''<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none"><path fill="#fff" d="M16 3C8.82 3 3 8.46 3 15.16c0 3.66 1.78 6.92 4.58 9.16v4.51l4.27-2.35c1.18.32 2.42.5 3.7.5 7.18 0 13-5.46 13-12.16C29 8.46 23.18 3 16 3Zm1.34 16.6-3.32-3.55-6.27 3.55 6.9-7.3 3.36 3.55 6.23-3.55-6.9 7.3Z"/></svg>''',

    # 4. OpenAI / ChatGPT (knot / pétalas estilizadas)
    'OpenAI': '''<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none"><path fill="#fff" d="M29.71 13.4a7.36 7.36 0 0 0-.63-6.04 7.45 7.45 0 0 0-8.03-3.58A7.41 7.41 0 0 0 15.5 1.34a7.45 7.45 0 0 0-7.1 5.16 7.42 7.42 0 0 0-4.96 3.6 7.45 7.45 0 0 0 .91 8.74 7.36 7.36 0 0 0 .64 6.04 7.45 7.45 0 0 0 8.02 3.58 7.4 7.4 0 0 0 5.56 2.48 7.45 7.45 0 0 0 7.1-5.16 7.42 7.42 0 0 0 4.95-3.6 7.45 7.45 0 0 0-.91-8.78Zm-11.1 15.49a5.52 5.52 0 0 1-3.55-1.28c.05-.02.13-.07.17-.1l5.84-3.37a.95.95 0 0 0 .48-.83v-8.23l2.47 1.43a.09.09 0 0 1 .05.07v6.81a5.55 5.55 0 0 1-5.46 5.5Zm-11.74-5.01a5.5 5.5 0 0 1-.66-3.7c.05.03.13.08.18.1l5.84 3.38a.95.95 0 0 0 .96 0l7.13-4.12v2.85a.09.09 0 0 1-.04.08l-5.9 3.41a5.54 5.54 0 0 1-7.51-2.02Zm-1.54-12.79a5.5 5.5 0 0 1 2.89-2.42v6.93a.94.94 0 0 0 .48.83l7.12 4.11-2.46 1.42a.09.09 0 0 1-.08 0l-5.91-3.41a5.55 5.55 0 0 1-2.04-7.46Zm20.27 4.71-7.12-4.12 2.46-1.42a.09.09 0 0 1 .08 0l5.91 3.41a5.54 5.54 0 0 1-.83 10.01v-6.94a.94.94 0 0 0-.5-.94Zm2.45-3.68a4.8 4.8 0 0 0-.17-.1l-5.84-3.38a.95.95 0 0 0-.96 0L13.95 12.7V9.85a.09.09 0 0 1 .04-.08l5.9-3.41a5.54 5.54 0 0 1 8.21 5.74Zm-15.45 5.07-2.47-1.43a.09.09 0 0 1-.05-.07V8.84a5.54 5.54 0 0 1 9.08-4.27c-.04.02-.13.07-.17.1l-5.84 3.37a.95.95 0 0 0-.48.83l-.07 8.23Zm1.34-2.89L16 11.43l3.06 1.77v3.54L16 18.51l-3.06-1.77V13.2Z"/></svg>''',

    # 5. Google Gemini (estrela 4-pontas)
    'Gemini': '''<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none"><path fill="#fff" d="M16 1.6c0 8.66-5.74 14.4-14.4 14.4 8.66 0 14.4 5.74 14.4 14.4 0-8.66 5.74-14.4 14.4-14.4-8.66 0-14.4-5.74-14.4-14.4Z"/></svg>''',

    # 6. Dialogflow (3 balões sobrepostos)
    'Dialogflow': '''<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none"><path fill="#fff" d="M16 4 4 11v10l12 7 12-7V11L16 4Zm0 2.31 9.93 5.8L16 17.91 6.07 12.11 16 6.31Zm-10 7.5 9 5.25v8.59l-9-5.25v-8.59Zm11 13.84v-8.59l9-5.25v8.59l-9 5.25Z"/></svg>''',

    # 7. Typebot (bot com olhos)
    'Typebot': '''<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none"><path fill="#fff" d="M14 1.5v3.07A11.27 11.27 0 0 0 3.5 15.78v8.43A5.29 5.29 0 0 0 8.78 29.5h14.44a5.29 5.29 0 0 0 5.28-5.29v-8.43A11.27 11.27 0 0 0 18 4.57V1.5h-4Zm-4.78 21a2.78 2.78 0 0 1-2.78-2.78v-3.93a8.78 8.78 0 0 1 17.56 0v3.93a2.78 2.78 0 0 1-2.78 2.78H9.22Zm2.78-7.5a2 2 0 1 0 2 2 2 2 0 0 0-2-2Zm8 0a2 2 0 1 0 2 2 2 2 0 0 0-2-2Z"/></svg>''',

    # 8. n8n (3 circles connected)
    'n8n': '''<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none"><circle cx="6" cy="16" r="3" fill="#fff"/><circle cx="16" cy="9" r="3" fill="#fff"/><circle cx="16" cy="23" r="3" fill="#fff"/><circle cx="26" cy="16" r="3" fill="#fff"/><path stroke="#fff" stroke-width="1.5" d="M9 16h4M19 9h4M19 23h4M16 12v8"/></svg>''',

    # 9. Webhooks (gancho/branching paths)
    'Webhooks': '''<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none"><path fill="#fff" d="M22 18a4 4 0 0 0-3.4 1.9l-3-5A6 6 0 1 0 8 16a3.5 3.5 0 0 1 .5 1.7l-4 6.6a4 4 0 1 0 2.6 1.5l5.5-9.1A4 4 0 1 1 14 14l5.6 9.3A4 4 0 1 0 22 18Zm-7.5-6.5a3 3 0 1 1 4-3.4l.7 1.2H22a3 3 0 1 1 0 6h-7.5l1.5-2.6A2.97 2.97 0 0 0 14.5 11.5ZM5 27a2 2 0 1 1 2-2 2 2 0 0 1-2 2Zm17 0a2 2 0 1 1 2-2 2 2 0 0 1-2 2Z"/></svg>''',

    # 10. Cal.com (calendário)
    'Cal.com': '''<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none"><rect x="4" y="6" width="24" height="22" rx="3" stroke="#fff" stroke-width="2" fill="none"/><path stroke="#fff" stroke-width="2" stroke-linecap="round" d="M4 12h24M10 3v6M22 3v6"/><circle cx="16" cy="18" r="2" fill="#fff"/></svg>''',
}

LABELS_PT = {
    'WhatsApp': 'WhatsApp Oficial',
    'Instagram': 'Instagram',
    'Messenger': 'Facebook Messenger',
    'OpenAI': 'OpenAI / ChatGPT',
    'Gemini': 'Google Gemini',
    'Dialogflow': 'Google Dialogflow',
    'Typebot': 'Typebot',
    'n8n': 'n8n',
    'Webhooks': 'Webhooks',
    'Cal.com': 'Cal.com',
}

# Encode each SVG to base64 data URI
LOGO_DATA = {}
for name, svg in LOGOS.items():
    b64 = base64.b64encode(svg.encode('utf-8')).decode('ascii')
    LOGO_DATA[name] = f'data:image/svg+xml;base64,{b64}'

# Build a single logo card HTML
def card(name):
    src = LOGO_DATA[name]
    label = LABELS_PT[name]
    return (
        '<div class="flex shrink-0 items-center gap-2 rounded-lg bg-muted/50 '
        'border border-border/50 px-4 py-2.5 mx-2">'
        f'<img src="{src}" alt="{name}" class="h-7 w-auto opacity-80" loading="lazy">'
        f'<span class="text-sm font-medium text-foreground/80 whitespace-nowrap">{label}</span>'
        '</div>'
    )

# Order: visually balanced for marquee
ORDER = list(LOGOS.keys())

# Marquee track contents (duplicated 2x for seamless loop)
TRACK = ''.join(card(n) for n in ORDER) + ''.join(card(n) for n in ORDER)

# Now patch the HTML: find both marquee tracks and replace their contents
p = Path('infizap-lp-v1.html')
c = p.read_text(encoding='utf-8')
start = c.rfind('<section', 0, c.find('Integrações nativas:'))
end = c.find('</section>', start) + len('</section>')
seg = c[start:end]

def replace_marquee_track(seg, track_class_suffix, new_content):
    """Find <div class="flex animate-marquee-{suffix}" ...> and replace its inner."""
    pat = re.compile(rf'<div class="flex animate-marquee-{track_class_suffix}"[^>]*>')
    m = pat.search(seg)
    if not m:
        return seg, False
    open_end = m.end()
    # Walk to find matching </div>
    depth = 1
    pos = open_end
    while depth > 0 and pos < len(seg):
        nopen = seg.find('<div', pos)
        nclose = seg.find('</div>', pos)
        if nclose < 0:
            return seg, False
        if 0 <= nopen < nclose:
            depth += 1
            pos = nopen + 4
        else:
            depth -= 1
            pos = nclose + 6
    return seg[:open_end] + new_content + seg[pos-6:], True

seg, ok_r = replace_marquee_track(seg, 'right', TRACK)
print(f'Marquee-right replaced: {ok_r}')
seg, ok_l = replace_marquee_track(seg, 'left', TRACK)
print(f'Marquee-left replaced: {ok_l}')

# Reassemble
new_c = c[:start] + seg + c[end:]
print(f'\nOld size: {len(c)} | New size: {len(new_c)} | Delta: {len(new_c) - len(c)}')

p.write_text(new_c, encoding='utf-8')

# Sanity check
print('\nFinal alt= values in section:')
seg2 = new_c[start:start + (end - start) + (len(new_c) - len(c))]
end2 = new_c.find('</section>', start) + len('</section>')
seg2 = new_c[start:end2]
alts = re.findall(r'alt="([^"]+)"', seg2)
from collections import Counter
for name, cnt in Counter(alts).items():
    print(f'  {name}: {cnt}')
