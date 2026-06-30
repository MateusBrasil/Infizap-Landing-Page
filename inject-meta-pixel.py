# -*- coding: utf-8 -*-
"""Injeta Meta Pixel (id 1754764649012594) logo após <head> em infizap-lp-v1.html.

Idempotente: se o snippet "Meta Pixel Code - INFIZAP" já estiver no arquivo, nada acontece.
"""
import io, sys, os

PATH = os.path.join(os.path.dirname(__file__), "infizap-lp-v1.html")
PIXEL_ID = "1754764649012594"
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

    if MARKER in html:
        print("[ok] Meta Pixel já presente — nada a fazer.")
        return 0

    if HEAD_MARKER not in html:
        print("[erro] Marcador do <head> não encontrado — arquivo mudou de forma?")
        return 1

    new_html = html.replace(HEAD_MARKER, HEAD_MARKER + "\n" + PIXEL_SNIPPET, 1)

    with io.open(PATH, "w", encoding="utf-8", newline="") as f:
        f.write(new_html)

    print(f"[ok] Meta Pixel ({PIXEL_ID}) injetado em infizap-lp-v1.html ({len(new_html):,} bytes).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
