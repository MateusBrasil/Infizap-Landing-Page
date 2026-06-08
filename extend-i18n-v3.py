"""Third batch — fix Spanish-leak in PT testimonials (Lieke, João)."""
import sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

PAIRS = [
    # Lieke van der Berg testimonial — first sentence is mixed PT/ES
    ('"Com INFIZAP logramos dar seguimiento real a nuestros clientes.',
     '"With INFIZAP we got real follow-up with our customers.',
     '"Con INFIZAP logramos dar seguimiento real a nuestros clientes.'),
    # Plain PT version of the same sentence (in case extra walker pass strips the quote first)
    ('Com INFIZAP logramos dar seguimiento real a nuestros clientes.',
     'With INFIZAP we got real follow-up with our customers.',
     'Con INFIZAP logramos dar seguimiento real a nuestros clientes.'),

    # João/Lucas testimonial — last sentence is in Spanish (leak)
    ('. En cuestión de una hora ya estaba creando mis primeros flujos y viendo resultados reales en mi negocio.',
     '. Within an hour I was already creating my first flows and seeing real results in my business.',
     '. En cuestión de una hora ya estaba creando mis primeros flujos y viendo resultados reales en mi negocio.'),
    ('En cuestión de una hora ya estaba creando mis primeros flujos y viendo resultados reales en mi negocio.',
     'Within an hour I was already creating my first flows and seeing real results in my business.',
     'En cuestión de una hora ya estaba creando mis primeros flujos y viendo resultados reales en mi negocio.'),
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

print(f'Batch v3 — {len(PAIRS)} pairs')
print(f'  added en: {added_en}')
print(f'  added es: {added_es}')
print(f'  overwritten: {overwritten}')
print(f'Total: en={len(en)}, es={len(es)}, pt-BR={len(ptbr)}')
