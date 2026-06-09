"""
Rebuild pricing cards from scratch to match INTEGRACOES E CONFIG DE PLANOS doc.

Strategy:
1. Find each card's <ul class="pricing-features">...</ul> block
2. Replace its inner content with a freshly-generated list aligned to the doc
3. Also fix copy bugs: INCLUIDA→INCLUÍDA, SOPORTE→SUPORTE, tooltips ES→PT, €97 USD→€97
"""
import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

p = Path('infizap-lp-v1.html')
c = p.read_text(encoding='utf-8')

# Standard icons (copied from existing pricing-features)
ICON_CHECK = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
    'stroke-linejoin="round" class="pricing-feature-icon pricing-feature-icon--primary" '
    'data-astro-cid-7jt2x4ie=""><polyline points="20 6 9 17 4 12" data-astro-cid-7jt2x4ie="">'
    '</polyline></svg>'
)
ICON_X = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
    'stroke-linejoin="round" class="pricing-feature-icon pricing-feature-icon--x" '
    'data-astro-cid-7jt2x4ie=""><path d="M18 6 6 18" data-astro-cid-7jt2x4ie=""></path>'
    '<path d="m6 6 12 12" data-astro-cid-7jt2x4ie=""></path></svg>'
)
SUPPORT_ICON = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
    'stroke-linejoin="round" data-astro-cid-7jt2x4ie="">'
    '<path d="M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a9 9 0 0 1 18 0v7a2 '
    '2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3" data-astro-cid-7jt2x4ie=""></path></svg>'
)

def li(text, active=True):
    icon = ICON_CHECK if active else ICON_X
    cls = "pricing-feature" if active else "pricing-feature pricing-feature--disabled"
    return (
        f'<li class="{cls}" data-astro-cid-7jt2x4ie="">{icon}'
        f'<span data-astro-cid-7jt2x4ie="">{text}</span></li>'
    )

def li_highlight(text, color="#7EE8FA"):
    """Active li with highlighted accent text."""
    return (
        f'<li class="pricing-feature" data-astro-cid-7jt2x4ie="">{ICON_CHECK}'
        f'<span data-astro-cid-7jt2x4ie="">{text}</span></li>'
    )

def support_badge(label, premium=False):
    cls = "soporte-badge soporte-badge--premium" if premium else "soporte-badge"
    return (
        f'<li class="pricing-feature pricing-feature--soporte" data-astro-cid-7jt2x4ie="">'
        f'<span class="{cls}" data-astro-cid-7jt2x4ie="">{SUPPORT_ICON}{label}</span></li>'
    )

# === START €47 features ===
START_FEATURES = [
    li('<span style="color:#7EE8FA;font-weight:700;">3</span> usuários'),
    li('<span style="color:#7EE8FA;font-weight:700;">1</span> canal WhatsApp'),
    li('<span style="color:#7EE8FA;font-weight:700;">2</span> filas / setores'),
    li('CRM + Kanban'),
    li('Chatbot + Flow Builder visual'),
    li('Agendamento de mensagens'),
    li('Respostas rápidas'),
    li('Chat interno entre atendentes'),
    li('Tags + Carteira de contatos'),
    li('NPS / avaliação de atendimento'),
    li('Transcrição de áudio recebido'),
    li('LGPD (consentimento · ocultar número)'),
    li('Backup em nuvem'),
    li('Relatórios + exportação Excel/PDF'),
    support_badge('SUPORTE PADRÃO'),
    li('Instagram + Facebook', active=False),
    li('Campanhas de disparo em massa', active=False),
    li('Integrações (Typebot · n8n · Dialogflow · Cal.com)', active=False),
    li('Agente de IA', active=False),
    li('API REST aberta', active=False),
    li('API Oficial do WhatsApp (Meta)', active=False),
    li('Ligação por WhatsApp · gravação', active=False),
]

# === PRO €97 features ===
PRO_FEATURES = [
    li('<span style="color:#7EE8FA;font-weight:700;">5</span> usuários'),
    li('<span style="color:#7EE8FA;font-weight:700;">2</span> canais conectados'),
    li('<span style="color:#7EE8FA;font-weight:700;">5</span> filas / setores'),
    li('WhatsApp + Instagram + Facebook'),
    li('CRM + Kanban'),
    li('Chatbot + Flow Builder visual'),
    li('Agendamento de mensagens'),
    li('Respostas rápidas'),
    li('Chat interno entre atendentes'),
    li('Tags + Carteira de contatos'),
    li('Campanhas de disparo em massa'),
    li('Integrações (Typebot · n8n · Dialogflow · Cal.com · Webhooks)'),
    li('NPS / avaliação de atendimento'),
    li('Transcrição de áudio recebido'),
    li('LGPD (consentimento · ocultar número)'),
    li('Backup em nuvem'),
    li('Relatórios + exportação Excel/PDF'),
    support_badge('SUPORTE PADRÃO'),
    li('Agente de IA', active=False),
    li('API REST aberta', active=False),
    li('API Oficial do WhatsApp (Meta)', active=False),
    li('Ligação por WhatsApp · gravação', active=False),
]

# === BUSINESS €197 features ===
BUSINESS_FEATURES = [
    li('<span style="color:#7EE8FA;font-weight:700;">10</span> usuários'),
    li('<span style="color:#7EE8FA;font-weight:700;">3</span> canais conectados'),
    li('<span style="color:#7EE8FA;font-weight:700;">15</span> filas / setores'),
    li('WhatsApp + Instagram + Facebook'),
    li('CRM + Kanban'),
    li('Chatbot + Flow Builder visual'),
    li('Agendamento de mensagens'),
    li('Respostas rápidas'),
    li('Chat interno entre atendentes'),
    li('Tags + Carteira de contatos'),
    li('Campanhas de disparo em massa'),
    li('Integrações (Typebot · n8n · Dialogflow · Cal.com · Webhooks)'),
    li('🤖 Desbloqueia o Agente de IA · créditos à parte'),
    li('API Oficial do WhatsApp (Meta)'),
    li('API REST aberta'),
    li('Ligação por WhatsApp · gravação (add-on €39/usuário)'),
    li('NPS / avaliação de atendimento'),
    li('Transcrição de áudio recebido'),
    li('LGPD (consentimento · ocultar número)'),
    li('Backup em nuvem'),
    li('Relatórios + exportação Excel/PDF'),
    support_badge('SUPORTE PREMIUM', premium=True),
]

def rebuild_card_ul(html, plan_name, new_features):
    """Find <ul class="pricing-features"> after h3 'Plano X', replace its content."""
    # Find h3 for this plan
    h3_pat = rf'<h3[^>]*class="pricing-plan-name"[^>]*>Plano\s+{re.escape(plan_name)}'
    h3_matches = list(re.finditer(h3_pat, html))
    if not h3_matches:
        print(f'  ! No h3 found for Plano {plan_name}')
        return html
    # Use the second match (visible monthly tab) — both tabs share the same ul afterwards
    # Actually each card has 1 ul that's between the prices and cta. Use first h3 occurrence as anchor.
    anchor = h3_matches[0].start()
    ul_start = html.find('<ul class="pricing-features"', anchor)
    if ul_start < 0:
        print(f'  ! No <ul class="pricing-features"> after Plano {plan_name}')
        return html
    # Find matching </ul>
    ul_open_end = html.find('>', ul_start) + 1
    ul_close = html.find('</ul>', ul_open_end)
    if ul_close < 0:
        print(f'  ! No closing </ul> for Plano {plan_name}')
        return html
    new_content = ''.join(new_features)
    new_html = html[:ul_open_end] + new_content + html[ul_close:]
    print(f'  ✓ {plan_name}: replaced ul (was {ul_close - ul_open_end} bytes, now {len(new_content)} bytes, {len(new_features)} items)')
    return new_html

print('Rebuilding card feature lists...')
c = rebuild_card_ul(c, 'Start',    START_FEATURES)
c = rebuild_card_ul(c, 'Pro',      PRO_FEATURES)
c = rebuild_card_ul(c, 'Business', BUSINESS_FEATURES)

# ===== COPY FIXES =====
print('\nCopy fixes...')
n = 0

# 1. INCLUIDA → INCLUÍDA (PT correct spelling)
before = c.count('INCLUIDA')
c = c.replace('>INCLUIDA<', '>INCLUÍDA<')
print(f'  INCLUIDA → INCLUÍDA: {before - c.count("INCLUIDA")} replaced')

# 2. SOPORTE → SUPORTE
before = c.count('SOPORTE PREMIUM')
c = c.replace('SOPORTE PREMIUM', 'SUPORTE PREMIUM')
print(f'  SOPORTE PREMIUM → SUPORTE PREMIUM: {before - c.count("SOPORTE PREMIUM")} replaced')

# 3. "€97 USD" → "€97" (drop USD - keep euro symbol)
before = c.count('€97 USD')
c = c.replace('€97 USD', '€97')
print(f'  €97 USD → €97: {before - c.count("€97 USD")} replaced')

# 4. Spanish tooltips → PT
# These appear in pricing-card info-tip data-tip="..."
es_tooltips = {
    'PUEDES AGREGAR MACs adicionales en este plan, para más información comunícate con nuestro equipo de soporte.':
        'Você pode adicionar mais usuários neste plano — fale com nosso time de suporte para mais informações.',
    'Puedes agregar números extra por €39 USD al mes por número adicional.':
        'Pode adicionar canais extras por €39/mês por canal adicional.',
    'Puedes agregar agentes humanos extra por €19 USD al mes por agente humano adicional.':
        'Pode adicionar usuários extras por €19/mês por usuário adicional.',
    'Crea tantos agentes como necesites. Base de conocimiento ilimitada con fuentes web, subida de archivos, bloques de texto, FAQs, Google Drive, YouTube, recursos multimedia y catálogo de productos.':
        'Crie quantos agentes precisar. Base de conhecimento ilimitada com fontes web, upload de arquivos, blocos de texto, FAQs, Google Drive, YouTube, mídias e catálogo de produtos.',
    'Preguntas Frecuentes, Cotizaciones, Ventas, Soporte al Cliente, Captación de Leads y Agendamiento de Citas. Incluye integración con Google Calendar, Calendly y Cal.com.':
        'FAQ, Orçamentos, Vendas, Suporte ao Cliente, Captação de Leads e Agendamento. Inclui integração com Google Calendar, Calendly e Cal.com.',
    'Incluye Sábados, domingos o festivos':
        'Inclui sábados, domingos e feriados.',
    'Asistente IA anti-bloqueos, moderación con IA en comunidades, variaciones de nombre con IA, condicionales de redirección, Link personalizado con dominio propio.':
        'Assistente IA anti-bloqueios, moderação com IA, variações de nome com IA, redirecionamento condicional e link personalizado com domínio próprio.',
}
total = 0
for es, pt in es_tooltips.items():
    n = c.count(es)
    if n > 0:
        c = c.replace(es, pt)
        total += n
        print(f'  ES tooltip ({n}x) translated: "{es[:60]}..."')
print(f'  Spanish tooltips translated: {total} total')

p.write_text(c, encoding='utf-8')
print(f'\nNew file size: {len(c)}')
