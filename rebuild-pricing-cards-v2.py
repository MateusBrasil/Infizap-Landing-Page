"""
Rebuild pricing cards V2 — ícones temáticos Lucide por feature
(em vez de check verde genérico).
"""
import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

p = Path('infizap-lp-v1.html')
c = p.read_text(encoding='utf-8')

ICON_CLASS = 'pricing-feature-icon pricing-feature-icon--primary'
SVG_ATTRS = (
    'xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
    'stroke-linejoin="round" data-astro-cid-7jt2x4ie=""'
)

def svg(paths_inner):
    """Build full SVG with primary icon class."""
    return f'<svg {SVG_ATTRS} class="{ICON_CLASS}">{paths_inner}</svg>'

def x_icon():
    return (
        f'<svg {SVG_ATTRS} class="pricing-feature-icon pricing-feature-icon--x">'
        '<path d="M18 6 6 18" data-astro-cid-7jt2x4ie=""></path>'
        '<path d="m6 6 12 12" data-astro-cid-7jt2x4ie=""></path></svg>'
    )

# Lucide icon paths (16x16 in 24x24 viewBox)
ICONS = {
    'users': '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    'smartphone': '<rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/>',
    'layers': '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>',
    'share': '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" x2="15.42" y1="13.51" y2="17.49"/><line x1="15.41" x2="8.59" y1="6.51" y2="10.49"/>',
    'kanban': '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M8 7v7"/><path d="M12 7v4"/><path d="M16 7v9"/>',
    'bot': '<path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/>',
    'calendar': '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
    'zap': '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    'message': '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
    'tag': '<path d="M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
    'send': '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
    'puzzle': '<path d="M15.39 4.39a1 1 0 0 0 1.68-.474 2.5 2.5 0 1 1 3.014 3.015 1 1 0 0 0-.474 1.68l1.683 1.682a2.414 2.414 0 0 1 0 3.414L19.61 15.39a1 1 0 0 1-1.68-.474 2.5 2.5 0 1 0-3.014 3.015 1 1 0 0 1 .474 1.68l-1.683 1.682a2.414 2.414 0 0 1-3.414 0L8.61 19.61a1 1 0 0 0-1.68.474 2.5 2.5 0 1 1-3.014-3.015 1 1 0 0 0 .474-1.68L2.707 13.707a2.414 2.414 0 0 1 0-3.414L4.39 8.61a1 1 0 0 1 1.68.474 2.5 2.5 0 1 0 3.014-3.015 1 1 0 0 1-.474-1.68l1.683-1.682a2.414 2.414 0 0 1 3.414 0z"/>',
    'sparkles': '<path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/>',
    'shield': '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    'code': '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
    'phone': '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
    'star': '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    'mic': '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/>',
    'lock': '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    'cloud': '<path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M12 12v9"/><path d="m16 16-4-4-4 4"/>',
    'chart': '<path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
    'flow': '<rect x="3" y="3" width="8" height="8" rx="2"/><rect x="13" y="13" width="8" height="8" rx="2"/><path d="M7 11v4a2 2 0 0 0 2 2h4"/>',
    'wallet': '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>',
    'megaphone': '<path d="m3 11 18-5v12L3 14v-3z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/>',
    'headset': '<path d="M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a9 9 0 0 1 18 0v7a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3"/>',
}

SUPPORT_ICON_INNER = ICONS['headset']

def li(icon_key, text, active=True):
    if not active:
        icon_svg = x_icon()
        cls = "pricing-feature pricing-feature--disabled"
    else:
        icon_svg = svg(ICONS[icon_key])
        cls = "pricing-feature"
    return (
        f'<li class="{cls}" data-astro-cid-7jt2x4ie="">{icon_svg}'
        f'<span data-astro-cid-7jt2x4ie="">{text}</span></li>'
    )

def support_badge(label, premium=False):
    cls = "soporte-badge soporte-badge--premium" if premium else "soporte-badge"
    support_svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round" data-astro-cid-7jt2x4ie="">{SUPPORT_ICON_INNER}</svg>'
    )
    return (
        f'<li class="pricing-feature pricing-feature--soporte" data-astro-cid-7jt2x4ie="">'
        f'<span class="{cls}" data-astro-cid-7jt2x4ie="">{support_svg}{label}</span></li>'
    )

ACCENT = 'color:#7EE8FA;font-weight:700;'

# === START ===
START_FEATURES = [
    li('users',      f'<span style="{ACCENT}">3</span> usuários'),
    li('smartphone', f'<span style="{ACCENT}">1</span> canal WhatsApp'),
    li('layers',     f'<span style="{ACCENT}">2</span> filas / setores'),
    li('kanban',     'CRM + Kanban'),
    li('flow',       'Chatbot + Flow Builder visual'),
    li('calendar',   'Agendamento de mensagens'),
    li('zap',        'Respostas rápidas'),
    li('message',    'Chat interno entre atendentes'),
    li('tag',        'Tags + Carteira de contatos'),
    li('star',       'NPS / avaliação de atendimento'),
    li('mic',        'Transcrição de áudio recebido'),
    li('lock',       'LGPD (consentimento · ocultar número)'),
    li('cloud',      'Backup em nuvem'),
    li('chart',      'Relatórios + exportação Excel/PDF'),
    support_badge('SUPORTE PADRÃO'),
    li('share',     'Instagram + Facebook', active=False),
    li('megaphone', 'Campanhas de disparo em massa', active=False),
    li('puzzle',    'Integrações (Typebot · n8n · Dialogflow · Cal.com)', active=False),
    li('sparkles',  'Agente de IA', active=False),
    li('code',      'API REST aberta', active=False),
    li('shield',    'API Oficial do WhatsApp (Meta)', active=False),
    li('phone',     'Ligação por WhatsApp · gravação', active=False),
]

# === PRO ===
PRO_FEATURES = [
    li('users',      f'<span style="{ACCENT}">5</span> usuários'),
    li('smartphone', f'<span style="{ACCENT}">2</span> canais conectados'),
    li('layers',     f'<span style="{ACCENT}">5</span> filas / setores'),
    li('share',      'WhatsApp + Instagram + Facebook'),
    li('kanban',     'CRM + Kanban'),
    li('flow',       'Chatbot + Flow Builder visual'),
    li('calendar',   'Agendamento de mensagens'),
    li('zap',        'Respostas rápidas'),
    li('message',    'Chat interno entre atendentes'),
    li('tag',        'Tags + Carteira de contatos'),
    li('megaphone',  'Campanhas de disparo em massa'),
    li('puzzle',     'Integrações (Typebot · n8n · Dialogflow · Cal.com · Webhooks)'),
    li('star',       'NPS / avaliação de atendimento'),
    li('mic',        'Transcrição de áudio recebido'),
    li('lock',       'LGPD (consentimento · ocultar número)'),
    li('cloud',      'Backup em nuvem'),
    li('chart',      'Relatórios + exportação Excel/PDF'),
    support_badge('SUPORTE PADRÃO'),
    li('sparkles',  'Agente de IA', active=False),
    li('code',      'API REST aberta', active=False),
    li('shield',    'API Oficial do WhatsApp (Meta)', active=False),
    li('phone',     'Ligação por WhatsApp · gravação', active=False),
]

# === BUSINESS ===
BUSINESS_FEATURES = [
    li('users',      f'<span style="{ACCENT}">10</span> usuários'),
    li('smartphone', f'<span style="{ACCENT}">3</span> canais conectados'),
    li('layers',     f'<span style="{ACCENT}">15</span> filas / setores'),
    li('share',      'WhatsApp + Instagram + Facebook'),
    li('kanban',     'CRM + Kanban'),
    li('flow',       'Chatbot + Flow Builder visual'),
    li('calendar',   'Agendamento de mensagens'),
    li('zap',        'Respostas rápidas'),
    li('message',    'Chat interno entre atendentes'),
    li('tag',        'Tags + Carteira de contatos'),
    li('megaphone',  'Campanhas de disparo em massa'),
    li('puzzle',     'Integrações (Typebot · n8n · Dialogflow · Cal.com · Webhooks)'),
    li('sparkles',   '🤖 Desbloqueia o Agente de IA · créditos à parte'),
    li('shield',     'API Oficial do WhatsApp (Meta)'),
    li('code',       'API REST aberta'),
    li('phone',      'Ligação por WhatsApp · gravação (add-on €39/usuário)'),
    li('star',       'NPS / avaliação de atendimento'),
    li('mic',        'Transcrição de áudio recebido'),
    li('lock',       'LGPD (consentimento · ocultar número)'),
    li('cloud',      'Backup em nuvem'),
    li('chart',      'Relatórios + exportação Excel/PDF'),
    support_badge('SUPORTE PREMIUM', premium=True),
]

def rebuild_card_ul(html, plan_name, new_features):
    h3_pat = rf'<h3[^>]*class="pricing-plan-name"[^>]*>Plano\s+{re.escape(plan_name)}'
    h3_matches = list(re.finditer(h3_pat, html))
    if not h3_matches:
        print(f'  ! No h3 for Plano {plan_name}')
        return html
    anchor = h3_matches[0].start()
    ul_start = html.find('<ul class="pricing-features"', anchor)
    if ul_start < 0:
        print(f'  ! No <ul> after Plano {plan_name}')
        return html
    ul_open_end = html.find('>', ul_start) + 1
    ul_close = html.find('</ul>', ul_open_end)
    new_content = ''.join(new_features)
    new_html = html[:ul_open_end] + new_content + html[ul_close:]
    print(f'  ✓ {plan_name}: {len(new_features)} items, {len(new_content)} bytes')
    return new_html

print('Rebuilding card features with thematic icons...')
c = rebuild_card_ul(c, 'Start',    START_FEATURES)
c = rebuild_card_ul(c, 'Pro',      PRO_FEATURES)
c = rebuild_card_ul(c, 'Business', BUSINESS_FEATURES)

p.write_text(c, encoding='utf-8')
print(f'\nFinal size: {len(c)}')
