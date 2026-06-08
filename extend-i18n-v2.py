"""Second massive batch — covers globe pins, chat bubbles, pricing internals, footer, nav."""
import sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

# (pt, en, es) — proper nouns and brand names keep PT form intact in EN/ES
PAIRS = [
    # === Globe pin labels (uppercase via CSS but stored as Title-case) ===
    ("Brasil", "Brazil", "Brasil"),
    ("Portugal", "Portugal", "Portugal"),
    ("Reino Unido", "United Kingdom", "Reino Unido"),
    ("Inglaterra", "England", "Inglaterra"),
    ("Suíça", "Switzerland", "Suiza"),
    ("Arábia Saudita", "Saudi Arabia", "Arabia Saudita"),
    ("Holanda", "Netherlands", "Países Bajos"),
    ("Espanha", "Spain", "España"),
    ("Argentina", "Argentina", "Argentina"),
    ("Chile", "Chile", "Chile"),
    ("EUA", "USA", "EE.UU."),
    ("Estados Unidos", "United States", "Estados Unidos"),

    # Globe timezone labels
    ("Lisboa · GMT+0", "Lisbon · GMT+0", "Lisboa · GMT+0"),
    ("Riade · GMT+3", "Riyadh · GMT+3", "Riad · GMT+3"),

    # === Chat bubbles ===
    ("Olá!", "Hi!", "¡Hola!"),

    # === Pricing internals ===
    ("Objetivos dos agentes:", "Agent objectives:", "Objetivos de los agentes:"),
    ("TODOS", "ALL", "TODOS"),
    ("SUPORTE PADRÃO", "STANDARD SUPPORT", "SOPORTE ESTÁNDAR"),
    ("SUPORTE PREMIUM", "PREMIUM SUPPORT", "SOPORTE PREMIUM"),
    ("SOPORTE PREMIUM", "PREMIUM SUPPORT", "SOPORTE PREMIUM"),
    ("Chat interno", "Internal chat", "Chat interno"),
    ("1 canal (WhatsApp/IG/FB)", "1 channel (WhatsApp/IG/FB)", "1 canal (WhatsApp/IG/FB)"),
    ("Canais conectados · WhatsApp · IG · FB",
     "Connected channels · WhatsApp · IG · FB",
     "Canales conectados · WhatsApp · IG · FB"),
    ("INCLUIDA", "INCLUDED", "INCLUIDA"),
    ("Gratis", "Free", "Gratis"),
    ("AGENTES DE IA", "AI AGENTS", "AGENTES DE IA"),
    ("Backup diário", "Daily backup", "Respaldo diario"),
    ("Beta · Brasil", "Beta · Brazil", "Beta · Brasil"),
    ("SLA · 90 dias", "SLA · 90 days", "SLA · 90 días"),

    # === 3-step section ===
    ("Conecte", "Connect", "Conecta"),
    ("Organize", "Organize", "Organiza"),
    ("Escale", "Scale", "Escala"),
    ("Ligue seus canais (WhatsApp, IG, Facebook) e importe seu histórico. Sem perder nada.",
     "Connect your channels (WhatsApp, IG, Facebook) and import your history. Without losing anything.",
     "Conecta tus canales (WhatsApp, IG, Facebook) e importa tu historial. Sin perder nada."),
    ("Sem perder nada.", "Without losing anything.", "Sin perder nada."),

    # === Concept block ===
    ("Com INFIZAP", "With INFIZAP", "Con INFIZAP"),
    ("Sem INFIZAP", "Without INFIZAP", "Sin INFIZAP"),
    ("Com estrutura", "With structure", "Con estructura"),
    ("Sem estrutura", "Without structure", "Sin estructura"),
    ("Comparativo", "Comparison", "Comparativa"),

    # === Quiz / form options ===
    ("Para quem é", "Who it's for", "Para quién es"),
    ("Sem dúvida:", "No doubt:", "Sin duda:"),
    ("Até 5", "Up to 5", "Hasta 5"),
    ("Até", "Up to", "Hasta"),
    ("Entre 5 e 15", "Between 5 and 15", "Entre 5 y 15"),
    ("Mais de 15", "More than 15", "Más de 15"),

    # === Industries ===
    ("Agências", "Agencies", "Agencias"),
    ("Agencias", "Agencies", "Agencias"),
    ("Saúde", "Healthcare", "Salud"),
    ("Educação", "Education", "Educación"),
    ("Serviços", "Services", "Servicios"),
    ("E-commerce", "E-commerce", "E-commerce"),
    ("Infoprodutores", "Info-product creators", "Infoproductores"),
    ("Comunidades", "Communities", "Comunidades"),
    ("SaaS", "SaaS", "SaaS"),

    # === Stats / labels ===
    ("Países ativos", "Active countries", "Países activos"),
    ("atendimentos", "conversations", "atenciones"),
    ("empresas", "companies", "empresas"),
    ("ecossistema", "ecosystem", "ecosistema"),
    ("Automatizações", "Automations", "Automatizaciones"),
    ("Omnichannel", "Omnichannel", "Omnicanal"),
    ("regiões AWS", "AWS regions", "regiones AWS"),
    ("Meta Partner", "Meta Partner", "Meta Partner"),

    # === Footer / nav ===
    ("Navegação", "Navigation", "Navegación"),
    ("Início", "Home", "Inicio"),
    ("Funcionalidades", "Features", "Funcionalidades"),
    ("Como funciona", "How it works", "Cómo funciona"),
    ("Sobre nós", "About us", "Sobre nosotros"),
    ("Aprender", "Learn", "Aprender"),
    ("Explorar", "Explore", "Explorar"),
    ("Blog", "Blog", "Blog"),
    ("Mapa do site", "Site map", "Mapa del sitio"),
    ("Termos de uso", "Terms of use", "Términos de uso"),
    ("Legal", "Legal", "Legal"),
    ("Novo", "New", "Nuevo"),
    ("Planos", "Plans", "Planes"),

    # === Form / nav ===
    ("Idioma", "Language", "Idioma"),
    ("Português (BR)", "Portuguese (BR)", "Portugués (BR)"),
    ("English", "English", "Inglés"),
    ("Español", "Spanish", "Español"),
    ("País", "Country", "País"),
    ("Entrar", "Sign in", "Entrar"),
    ("Começar", "Start", "Empezar"),
    ("ENVIAR", "SEND", "ENVIAR"),
    ("Volver", "Back", "Volver"),

    # === Pricing CTAs / labels ===
    ("EUR/ano", "EUR/year", "EUR/año"),
    ("anual", "annual", "anual"),

    # === Misc found in screenshots ===
    ("(MAC)", "(MAC)", "(MAC)"),
    ("&nbsp;", "&nbsp;", "&nbsp;"),
    ("Honesto", "Honest", "Honesto"),
    (", atende e vende", ", answers and sells", ", atiende y vende"),
    ("atende e vende", "answers and sells", "atiende y vende"),
    ("que antes me tomavam horas. Isso se traduz em",
     "that used to take me hours. That translates to",
     "que antes me tomaban horas. Eso se traduce en"),
    ("com o mesmo entusiasmo",
     "with the same enthusiasm",
     "con el mismo entusiasmo"),
    ("seu atendimento omnichannel",
     "your omnichannel customer service",
     "tu atención omnicanal"),
    ("INFIZAP — Mais vendas. Operação organizada. Números claros.",
     "INFIZAP — More sales. Organized operations. Clear numbers.",
     "INFIZAP — Más ventas. Operación organizada. Números claros."),
    ("Funciona com WhatsApp, Instagram e Facebook",
     "Works with WhatsApp, Instagram and Facebook",
     "Funciona con WhatsApp, Instagram y Facebook"),
    (". Ahora", ". Now", ". Ahora"),
    ("+1.2B", "+1.2B", "+1.2B"),
    ("+500M", "+500M", "+500M"),
    ("+1B", "+1B", "+1B"),
    ("+10k", "+10k", "+10k"),
    ("€97 USD", "€97 USD", "€97 USD"),

    # === Pricing CTAs and tooltips ===
    ("Continuar Comprando", "Continue shopping", "Continuar comprando"),
    ("Comprar agora", "Buy now", "Comprar ahora"),
    ("Sem fidelidade", "No commitment", "Sin permanencia"),

    # === Trust badges ===
    ("Compliance LGPD", "LGPD Compliance", "Cumplimiento LGPD"),
    ("LGPD", "LGPD", "LGPD"),
    ("API Oficial", "Official API", "API Oficial"),

    # === Pricing section misc ===
    ("Pago Único Anual", "Annual one-time payment", "Pago único anual"),
    ("Cobrança recorrente mensal · cancele quando quiser",
     "Monthly recurring billing · cancel anytime",
     "Cobro recurrente mensual · cancela cuando quieras"),
    ("Mensal", "Monthly", "Mensual"),
    ("Anual", "Annual", "Anual"),
    ("Economize", "Save", "Ahorra"),

    # === FAQ extras ===
    ("Sim", "Yes", "Sí"),
    ("Não", "No", "No"),

    # === Final ===
    ("Saiba mais", "Learn more", "Saber más"),
    ("Veja também", "See also", "Ver también"),
    ("Mostrar mais", "Show more", "Mostrar más"),
    ("Mostrar menos", "Show less", "Mostrar menos"),
]

en = json.loads(Path('i18n/en.json').read_text(encoding='utf-8'))
es = json.loads(Path('i18n/es.json').read_text(encoding='utf-8'))
ptbr = json.loads(Path('i18n/pt-BR.json').read_text(encoding='utf-8'))

added_en = 0; added_es = 0; overwritten = 0
for pt, en_t, es_t in PAIRS:
    if pt in en:
        if en[pt] != en_t:
            overwritten += 1
            en[pt] = en_t
    else:
        en[pt] = en_t
        added_en += 1
    if pt in es:
        if es[pt] != es_t:
            es[pt] = es_t
    else:
        es[pt] = es_t
        added_es += 1
    if pt not in ptbr:
        ptbr[pt] = pt

Path('i18n/en.json').write_text(json.dumps(en, ensure_ascii=False, indent=2), encoding='utf-8')
Path('i18n/es.json').write_text(json.dumps(es, ensure_ascii=False, indent=2), encoding='utf-8')
Path('i18n/pt-BR.json').write_text(json.dumps(ptbr, ensure_ascii=False, indent=2), encoding='utf-8')

print(f'Total pairs in this batch: {len(PAIRS)}')
print(f'  Added to en.json: {added_en}')
print(f'  Added to es.json: {added_es}')
print(f'  Overwritten: {overwritten}')
print(f'Total keys now: en={len(en)}, es={len(es)}, pt-BR={len(ptbr)}')
