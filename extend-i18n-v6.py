"""Batch v6 — labels das novas integrações."""
import sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

PAIRS = [
    ("WhatsApp Oficial",   "WhatsApp Official",  "WhatsApp Oficial",     "واتساب الرسمي"),
    ("Facebook Messenger", "Facebook Messenger", "Facebook Messenger",   "ماسنجر فيسبوك"),
    ("OpenAI / ChatGPT",   "OpenAI / ChatGPT",   "OpenAI / ChatGPT",     "OpenAI / ChatGPT"),
    ("Google Gemini",      "Google Gemini",      "Google Gemini",        "Google Gemini"),
    ("Google Dialogflow",  "Google Dialogflow",  "Google Dialogflow",    "Google Dialogflow"),
    ("Typebot",            "Typebot",            "Typebot",              "Typebot"),
    ("n8n",                "n8n",                "n8n",                  "n8n"),
    ("Webhooks",           "Webhooks",           "Webhooks",             "Webhooks"),
    ("Cal.com",            "Cal.com",            "Cal.com",              "Cal.com"),
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

print(f'Batch v6: {len(PAIRS)} labels, {added} new')
print(f'Total: en={len(en)}, es={len(es)}, ar={len(ar)}, pt-BR={len(ptbr)}')
