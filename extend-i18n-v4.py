"""Batch v4 — strings novas dos pricing cards revisados (€147, IA créditos, Wavoip)."""
import sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

PAIRS = [
    # Card descriptions adjusted
    ("WhatsApp (1 canal)", "WhatsApp (1 channel)", "WhatsApp (1 canal)", "واتساب (قناة واحدة)"),
    ("WhatsApp + Instagram + Facebook",
     "WhatsApp + Instagram + Facebook",
     "WhatsApp + Instagram + Facebook",
     "واتساب + إنستجرام + فيسبوك"),
    # Business IA new text
    ("🤖 Desbloqueia o Agente de IA · créditos à parte",
     "🤖 Unlocks the AI Agent · credits billed separately",
     "🤖 Desbloquea el Agente de IA · créditos por separado",
     "🤖 يفتح وكيل الذكاء الاصطناعي · أرصدة منفصلة"),
    # New Business features
    ("API Oficial do WhatsApp (Meta)",
     "WhatsApp Official API (Meta)",
     "API Oficial de WhatsApp (Meta)",
     "API الرسمي لواتساب (Meta)"),
    ("API REST aberta",
     "Open REST API",
     "API REST abierta",
     "API REST مفتوح"),
    ("Ligação por WhatsApp · gravação (add-on €39/usuário)",
     "WhatsApp calling · recording (add-on €39/user)",
     "Llamada por WhatsApp · grabación (add-on €39/usuario)",
     "مكالمات واتساب · تسجيل (إضافة €39/مستخدم)"),
    # Adjusted user counts
    ("3 acessos multiagente", "3 multi-agent accesses", "3 accesos multi-agente", "3 وصول متعدد الوكلاء"),
    ("5 acessos multiagente", "5 multi-agent accesses", "5 accesos multi-agente", "5 وصول متعدد الوكلاء"),
    ("10 acessos multiagente", "10 multi-agent accesses", "10 accesos multi-agente", "10 وصول متعدد الوكلاء"),
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

print(f'Batch v4: {len(PAIRS)} pairs, {added} truly new')
print(f'Total now: en={len(en)}, es={len(es)}, ar={len(ar)}, pt-BR={len(ptbr)}')
