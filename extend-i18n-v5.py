"""Batch v5 — todas as novas strings dos pricing cards reconstruídos."""
import sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

# (pt, en, es, ar)
PAIRS = [
    # Plan limits
    ("3 usuários", "3 users", "3 usuarios", "3 مستخدمين"),
    ("5 usuários", "5 users", "5 usuarios", "5 مستخدمين"),
    ("10 usuários", "10 users", "10 usuarios", "10 مستخدمين"),
    ("1 canal WhatsApp", "1 WhatsApp channel", "1 canal de WhatsApp", "قناة واتساب واحدة"),
    ("2 canais conectados", "2 connected channels", "2 canales conectados", "قناتان متصلتان"),
    ("3 canais conectados", "3 connected channels", "3 canales conectados", "3 قنوات متصلة"),
    ("2 filas / setores", "2 queues / departments", "2 colas / departamentos", "صفان / أقسام"),
    ("5 filas / setores", "5 queues / departments", "5 colas / departamentos", "5 صفوف / أقسام"),
    ("15 filas / setores", "15 queues / departments", "15 colas / departamentos", "15 صفاً / أقسام"),

    # Core features
    ("Chatbot + Flow Builder visual",
     "Chatbot + visual Flow Builder",
     "Chatbot + Flow Builder visual",
     "روبوت محادثة + منشئ التدفقات البصري"),
    ("Agendamento de mensagens", "Message scheduling", "Programación de mensajes", "جدولة الرسائل"),
    ("Chat interno entre atendentes",
     "Internal chat between agents",
     "Chat interno entre agentes",
     "محادثة داخلية بين الوكلاء"),
    ("Tags + Carteira de contatos",
     "Tags + Contact wallet",
     "Etiquetas + Cartera de contactos",
     "علامات + محفظة جهات الاتصال"),
    ("NPS / avaliação de atendimento",
     "NPS / service rating",
     "NPS / evaluación de atención",
     "NPS / تقييم الخدمة"),
    ("Transcrição de áudio recebido",
     "Received audio transcription",
     "Transcripción de audio recibido",
     "نسخ الصوت المستلم"),
    ("LGPD (consentimento · ocultar número)",
     "GDPR (consent · hide number)",
     "LGPD (consentimiento · ocultar número)",
     "LGPD (الموافقة · إخفاء الرقم)"),
    ("Backup em nuvem", "Cloud backup", "Respaldo en la nube", "نسخ احتياطي سحابي"),
    ("Relatórios + exportação Excel/PDF",
     "Reports + Excel/PDF export",
     "Informes + exportación Excel/PDF",
     "تقارير + تصدير Excel/PDF"),

    # Marketing/Integrations (Pro+)
    ("Campanhas de disparo em massa",
     "Mass broadcast campaigns",
     "Campañas de envío masivo",
     "حملات الإرسال الجماعي"),
    ("Integrações (Typebot · n8n · Dialogflow · Cal.com)",
     "Integrations (Typebot · n8n · Dialogflow · Cal.com)",
     "Integraciones (Typebot · n8n · Dialogflow · Cal.com)",
     "تكاملات (Typebot · n8n · Dialogflow · Cal.com)"),
    ("Integrações (Typebot · n8n · Dialogflow · Cal.com · Webhooks)",
     "Integrations (Typebot · n8n · Dialogflow · Cal.com · Webhooks)",
     "Integraciones (Typebot · n8n · Dialogflow · Cal.com · Webhooks)",
     "تكاملات (Typebot · n8n · Dialogflow · Cal.com · Webhooks)"),

    # Business-only
    ("Agente de IA", "AI Agent", "Agente de IA", "وكيل الذكاء الاصطناعي"),
    ("API REST aberta", "Open REST API", "API REST abierta", "API REST مفتوح"),
    ("Ligação por WhatsApp · gravação",
     "WhatsApp calling · recording",
     "Llamada por WhatsApp · grabación",
     "مكالمات واتساب · تسجيل"),
    ("Instagram + Facebook", "Instagram + Facebook", "Instagram + Facebook", "إنستجرام + فيسبوك"),

    # Already known but ensure presence
    ("SUPORTE PREMIUM", "PREMIUM SUPPORT", "SOPORTE PREMIUM", "دعم بريميوم"),
    ("INCLUÍDA", "INCLUDED", "INCLUIDA", "مشمولة"),
]

en = json.loads(Path('i18n/en.json').read_text(encoding='utf-8'))
es = json.loads(Path('i18n/es.json').read_text(encoding='utf-8'))
ar = json.loads(Path('i18n/ar.json').read_text(encoding='utf-8'))
ptbr = json.loads(Path('i18n/pt-BR.json').read_text(encoding='utf-8'))

added = 0
for pt, en_t, es_t, ar_t in PAIRS:
    if pt not in en: en[pt] = en_t; added += 1
    else: en[pt] = en_t
    if pt not in es: es[pt] = es_t
    else: es[pt] = es_t
    if pt not in ar: ar[pt] = ar_t
    else: ar[pt] = ar_t
    if pt not in ptbr: ptbr[pt] = pt

Path('i18n/en.json').write_text(json.dumps(en, ensure_ascii=False, indent=2), encoding='utf-8')
Path('i18n/es.json').write_text(json.dumps(es, ensure_ascii=False, indent=2), encoding='utf-8')
Path('i18n/ar.json').write_text(json.dumps(ar, ensure_ascii=False, indent=2), encoding='utf-8')
Path('i18n/pt-BR.json').write_text(json.dumps(ptbr, ensure_ascii=False, indent=2), encoding='utf-8')

print(f'Batch v5: {len(PAIRS)} pairs, {added} new')
print(f'Total: en={len(en)}, es={len(es)}, ar={len(ar)}, pt-BR={len(ptbr)}')
