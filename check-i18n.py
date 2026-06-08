"""Check coverage of i18n dicts."""
import sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

en = json.loads(Path('i18n/en.json').read_text(encoding='utf-8'))
es = json.loads(Path('i18n/es.json').read_text(encoding='utf-8'))

print(f'en keys: {len(en)}, es keys: {len(es)}')
print()
checks = ['Escale','Conecte','Olá!','Beleza, anotado!','SUPORTE PADRÃO',
         'TODOS','Termos de uso','Reino Unido','Inglaterra','Suíça',
         'Arábia Saudita','Brasil','Portugal','SUPORTE PREMIUM','SOPORTE PREMIUM',
         'Conecte seus canais (WhatsApp, IG, Facebook) e importe seu histórico.',
         'Sem perder nada.','Chat interno','1 canal (WhatsApp/IG/FB)',
         'Início','Funcionalidades','Como funciona','Depoimentos','Preços','FAQ']
for s in checks:
    if s in en:
        print(f'OK   "{s}" -> "{en[s]}"')
    else:
        print(f'MISS "{s}"')
