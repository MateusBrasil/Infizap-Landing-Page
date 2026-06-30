# -*- coding: utf-8 -*-
"""Configura o Meta Pixel da Infizap LP em infizap-lp-v1.html.

Faz duas coisas (ambas idempotentes):
1. Injeta o Meta Pixel oficial (id 1754764649012594) logo após <head>.
2. Neutraliza o pixel antigo (407533577279582) embutido no GTM herdado do
   site infizap.com original via mirror Umbrella — esse pixel mandava
   eventos pra um Business Manager que não é o do Mateus.

Rodar sempre que o mirror for regenerado:  python inject-meta-pixel.py
"""
import io, sys, os

PATH = os.path.join(os.path.dirname(__file__), "infizap-lp-v1.html")
PIXEL_ID = "1754764649012594"
OLD_PIXEL_ID = "407533577279582"
MARKER = "<!-- Meta Pixel Code - INFIZAP -->"

PIXEL_SNIPPET = f"""{MARKER}
<script>
!function(f,b,e,v,n,t,s)
{{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '{PIXEL_ID}');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id={PIXEL_ID}&ev=PageView&noscript=1"
/></noscript>
<!-- End Meta Pixel Code - INFIZAP -->
"""

# Marcador único no início do arquivo (mirror Umbrella).
HEAD_MARKER = '<head><!-- Umbrella Mirror build=2026-05-26-fix41-update-notifications mode=offline source=https://infizap.com/ -->'

def main():
    with io.open(PATH, "r", encoding="utf-8") as f:
        html = f.read()

    changed = False

    # 1) Injeta pixel oficial (idempotente via MARKER)
    if MARKER in html:
        print(f"[ok] Pixel {PIXEL_ID} já presente.")
    else:
        if HEAD_MARKER not in html:
            print("[erro] Marcador do <head> não encontrado — arquivo mudou de forma?")
            return 1
        html = html.replace(HEAD_MARKER, HEAD_MARKER + "\n" + PIXEL_SNIPPET, 1)
        changed = True
        print(f"[ok] Pixel {PIXEL_ID} injetado.")

    # 2) Neutraliza pixel antigo herdado do GTM do mirror.
    #    Passo A: trocar o ID literal por "0" nas constantes do GTM.
    #    Passo B: esvaziar o vtp_html das Custom HTML Tags do GTM que injetam
    #    o snippet completo do pixel (init+track+noscript). Sem isso, mesmo
    #    com ID=0 o Pixel Helper ainda detecta a chamada fbq('init','0').
    import re

    occurrences = html.count(OLD_PIXEL_ID)
    if occurrences > 0:
        html = html.replace(OLD_PIXEL_ID, "0")
        changed = True
        print(f"[ok] ID antigo {OLD_PIXEL_ID} → 0 em {occurrences} ocorrência(s).")

    # Esvazia qualquer vtp_html que carregue fbevents.js (snippets do pixel).
    # Padrão de string JSON: (?:[^"\\]|\\.)*? — non-greedy, respeita escapes.
    pat = re.compile(r'"vtp_html":"((?:[^"\\]|\\.)*?fbevents\.js(?:[^"\\]|\\.)*?)"')
    n_html = 0
    def _replace(m):
        nonlocal n_html
        n_html += 1
        return '"vtp_html":""'
    html = pat.sub(_replace, html)
    if n_html > 0:
        changed = True
        print(f"[ok] vtp_html do pixel esvaziado em {n_html} tag(s) do GTM.")

    # Passo C: desabilita o <script> que carrega o GTM container inteiro.
    # O GTM tem templates internos (__cvt_*) que injetam fbevents.js via JS —
    # esvaziar vtp_html nao basta. Mudar o type pra text/plain faz o browser
    # ignorar o script. Idempotente: so age se ainda não tem o marcador.
    gtm_old = '<script async="" data-umb2-entry-src="https://www.googletagmanager.com/gtm.js?id=GTM-T54P7M6Q">'
    gtm_new = '<script async="" data-umb2-entry-src="https://www.googletagmanager.com/gtm.js?id=GTM-T54P7M6Q" type="text/plain" data-disabled-by="infizap-lp">'
    if gtm_old in html:
        html = html.replace(gtm_old, gtm_new, 1)
        changed = True
        print(f"[ok] Script GTM-T54P7M6Q desabilitado (type=text/plain).")
    elif gtm_new in html:
        print(f"[ok] Script GTM-T54P7M6Q já estava desabilitado.")
    else:
        print(f"[!] Padrão do <script> GTM não encontrado — pode ter mudado de forma.")

    if not changed:
        print("[ok] Nada a fazer.")
        return 0

    with io.open(PATH, "w", encoding="utf-8", newline="") as f:
        f.write(html)
    print(f"[ok] Arquivo salvo ({len(html):,} bytes).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
