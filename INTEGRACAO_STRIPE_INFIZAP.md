# Integração Stripe → INFIZAP (criação automática de empresa)

Quando alguém compra um plano (mensal ou anual) na landing e a Stripe aprova,
o webhook cria a empresa do cliente no infizap **já com o plano certo** — sozinho, 24h.

```
Cliente clica no plano → preenche nome/telefone/email (modal) → Stripe Payment Link
        │ paga e aprova
        ▼
Stripe → checkout.session.completed  →  /api/stripe-webhook  (seu site na Vercel)
        │  valida assinatura · detecta o plano (price) · loga admin · cria empresa
        ▼
Empresa criada em app.infizap.com  ✅   +   cliente cai em /obrigado.html
```

> O que cria a empresa é o **webhook (servidor)**, não a página /obrigado.
> Assim funciona mesmo se o cliente fechar a aba depois de pagar.

---

## Arquivos desta integração (já no seu repo)
- `api/stripe-webhook.js` — a função serverless (o webhook).
- `package.json` — declara a dependência `stripe` (a Vercel instala no deploy).
- `.env.example` — modelo das variáveis de ambiente.

---

## Checklist pra ligar (na ordem)

> **Já feito:** Payment Links dos 6 planos criados e integrados na landing.
> Os 6 planos criados no infizap e já ligados no webhook (`PLAN_BY_AMOUNT`).
> O webhook reconhece o plano pelo **valor pago** (€47/€470/€97/€970/€197/€1970)
> — não precisa de Price IDs. Os benefícios de cada plano podem ser editados a
> qualquer momento no painel.

### 1. (FEITO) Planos no infizap e planId no webhook
| Plano | Mensal (planId) | Anual (planId) |
|---|---|---|
| Start | 4 | 7 |
| Pro | 5 | 8 |
| Business | 6 | 9 |

O vencimento da empresa é calculado automático: +30 dias (mensal) ou +365 (anual).

### 2. Redirect dos Payment Links → /obrigado (conferir)
Em cada Payment Link da Stripe, confirme **Após o pagamento → Redirecionar** para
`https://SEU-DOMINIO/obrigado.html` e ative **coletar telefone** (pra empresa
nascer com o telefone). A landing já repassa `prefilled_email` + `client_reference_id`.

### 3. Variáveis de ambiente na Vercel
Settings → Environment Variables (valores em `.env.example`):
`STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `INFIZAP_API_BASE`,
`INFIZAP_ADMIN_EMAIL`, `INFIZAP_ADMIN_PASSWORD`.

### 4. Publicar
```bash
git add . && git commit -m "webhook stripe -> infizap" && git push
```
Endpoint final: `https://SEU-DOMINIO/api/stripe-webhook`

### 5. Registrar o webhook na Stripe
Stripe → **Developers → Webhooks → Add endpoint**
- URL: `https://SEU-DOMINIO/api/stripe-webhook`
- Evento: `checkout.session.completed`
- Copie o **Signing secret** (`whsec_...`) → cole em `STRIPE_WEBHOOK_SECRET` → Redeploy.

### 6. Testar
Stripe → Webhooks → **Send test webhook**, ou compra em modo teste.
Logs em Vercel → Deployments → Functions. Confira a empresa em
`app.infizap.com/companies`.

---

## Entrega de credenciais ao cliente (falta você decidir)
A empresa é criada com o **email do cliente** e uma **senha aleatória**. Escolha como
o cliente recebe o acesso:
- **A) E-mail de boas-vindas (recomendado)** — habilitar `sendWelcomeEmail` no webhook + um provedor (Resend/SendGrid).
- **B) "Esqueci minha senha"** — na /obrigado, mandar o cliente logar e redefinir a senha no 1º acesso.
- **C) Mostrar na /obrigado** — menos seguro.

Me diga qual você quer que eu finalizo.

---

## Observações
- **Não duplica:** se já existir empresa com o mesmo email, o webhook pula.
- **Segurança:** recomendo um **usuário admin dedicado** do infizap só pra automação (não seu login pessoal).
- **Empresa de teste:** deixei a `id 5 "TESTE-AUTOMACAO"` no painel — apague quando quiser.
- **Stripe ao vivo:** use as chaves `live` no lançamento (e Payment Links no modo live).
