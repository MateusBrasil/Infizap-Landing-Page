# INFIZAP — Integrações reais + Configuração dos planos (para o desenvolvedor)

> Documento técnico de handoff · 09/jun/2026 · Hormozi Chief
> Fonte da verdade: leitura do **código-fonte real** em `CÓDIGO FONTE/WhiteLabel-zynca/` cruzada com a página atual (infizap.vercel.app) e o doc de oferta/preço.
> Objetivo: (1) corrigir a seção de integrações da página para refletir o que o sistema REALMENTE faz; (2) configurar os 3 planos dentro do sistema com os parâmetros exatos.

---

## ⚠️ LEIA PRIMEIRO — 3 descasamentos entre a PÁGINA e o SISTEMA

1. **"Créditos de IA" NÃO existem no sistema hoje.** A página/oferta vende "créditos de IA básicos" (Pro) e "agentes de IA" (Business). No código, IA é só uma **flag liga/desliga** (`useOpenAi`). Não há medidor de créditos, nem níveis básico/intermediário/avançado. → **Decisão necessária:** ou (a) vender IA como on/off por plano agora e tratar créditos como roadmap, ou (b) construir o sistema de créditos antes do go-live. Ver §3.
2. **API Oficial da Meta existe e é um microserviço à parte** (`api_oficial`, flag `useWhatsappOfficial`). Precisa decidir em qual plano ela entra. Ver §2.
3. **Transcrição:** a página coloca "transcrição de ligações" como roadmap (jul/2026) — correto. MAS **transcrição de áudio (mensagens de voz) já existe e funciona** (Google Speech, grátis). Pode anunciar isso como recurso atual. Ver §1.E.

---

# 1. INTEGRAÇÕES REAIS (confirmadas no código)

Tudo abaixo tem evidência no código. Dividido por categoria. **A seção "Integrações nativas" da página deve mostrar só o grupo voltado ao cliente (A, B, C, D, F) — não os gateways de pagamento (que são a cobrança do próprio INFIZAP) nem a infra.**

## A. Canais de atendimento (omnichannel) — o coração do produto
| Integração | Status | Evidência |
|---|---|---|
| **WhatsApp (QR Code / não oficial)** via Baileys | ✅ Real | `backend` `@whiskeysockets/baileys`, `libs/wbot.ts` |
| **WhatsApp API Oficial (Meta Cloud API)** | ✅ Real | microserviço `api_oficial` (NestJS), `phone_number_id`/`waba_id` |
| **Instagram Direct** | ✅ Real | `FacebookServices/graphAPI.ts` (graph.facebook.com), flag `useInstagram` |
| **Facebook Messenger** | ✅ Real | mesma graph API, flag `useFacebook` |

> Provedores alternativos de WhatsApp existem no código (NotificameHub, UAZAPI) mas são internos — **não mostrar como integração ao cliente.**

## B. Inteligência Artificial
| Integração | Status | Evidência |
|---|---|---|
| **OpenAI (ChatGPT)** | ✅ Real | `openai ^4.24.7`, `OpenAiService.ts`, flag `useOpenAi` |
| **Google Gemini** | ✅ Real | `@google/generative-ai`, mesmo service (`provider: openai \| gemini`) |
| **Google Dialogflow** | ✅ Real | `@google-cloud/dialogflow`, `QueryDialogflow.ts` |
| **Voz / TTS** (IA fala) | ✅ Real | OpenAI TTS + Microsoft Azure Speech SDK |

## C. Automação / no-code / API
| Integração | Status | Evidência |
|---|---|---|
| **Typebot** | ✅ Real | `TypebotServices/` (versão Baileys e oficial) |
| **n8n** | ✅ Real | campo `urlN8N` em `Integrations`/`QueueIntegrations` |
| **Webhooks + Flow Builder visual** | ✅ Real | `FlowBuilder.ts` (reactflow), `WebhookService/` |
| **API aberta (REST) para terceiros** | ✅ Real | `routes/apiRoutes.ts` (`/send`, `/checkNumber`), flag `useExternalApi` |
| **Chatwoot** | 🟡 Parcial | só referenciado no `api_oficial` (não há listener no backend Baileys) — **não anunciar como "nativo" ainda** |

## D. Agendamento (calendário)
| Integração | Status | Evidência |
|---|---|---|
| **Cal.com** | ✅ Real | `CalComService/CalComApiService.ts`, `CalComIntegration.ts` |
| Google Calendar/Drive | 🟡 Parcial | `googleapis` presente, usado p/ backup; agendamento Google não confirmado |

## E. Voz / Ligação
| Integração | Status | Evidência |
|---|---|---|
| **Wavoip (ligação por WhatsApp + gravação)** | ✅ Real | `wavoip-api`, `react-softphone`, `CallHistory.ts`, flag `wavoip` |
| **Transcrição de áudio (mensagens de voz)** | ✅ Real (hoje) | `TranscribeAudioMessageService` → microserviço Python (Google Speech grátis). **NÃO é Whisper pago.** |

## F. Pagamentos — cobrança das assinaturas (INTERNO, não é integração do cliente)
São os meios pelos quais o INFIZAP cobra o cliente. Bom ter vários, mas **não vão na barra de "integrações nativas" do produto.**
- ✅ **Stripe** · ✅ **Mercado Pago** · ✅ **Asaas** · ✅ **Gerencianet/Efí (Pix)**

## G. Infraestrutura (NÃO mostrar como integração)
E-mail SMTP (Nodemailer), Backup em nuvem (AWS S3 / MinIO / Google Drive / Dropbox), Supabase, Redis (filas), RabbitMQ, Sentry.

## ❌ NÃO existe no código (não anunciar)
- **Pagar.me** (não consta) · **OpenAI Whisper** (transcrição é Google grátis) · **OneSignal** (lib no frontend mas sem uso ativo).

---

# 2. FUNCIONALIDADES REAIS (o que listar como "o que você tem hoje")

Todas confirmadas em rotas/models do código:
- **Multiatendimento / multiusuário / multiempresa** (SaaS multi-tenant)
- **Filas / setores** + distribuição automática (`Queue`, `UserQueue`)
- **Chatbot + Flow Builder visual** (nodes JSON, condicional, randomizador, delay, handoff humano)
- **Kanban / CRM** (`react-trello`, flag `useKanban`)
- **Campanhas / disparo em massa** (até 5 msgs + 5 de confirmação, variáveis, agendamento, mídia — `Campaign.ts`)
- **Agendamento de mensagens** (`Schedule.ts`, flag `useSchedules`)
- **Respostas rápidas** (`QuickMessage`)
- **Tags** + **Carteira de contatos** (cliente volta pro mesmo atendente)
- **Chat interno entre atendentes** (flag `useInternalChat`)
- **API externa REST** (flag `useExternalApi`)
- **Prompts de IA / assistente** (`Prompt.ts`: apiKey, maxTokens, temperature, voice)
- **NPS / avaliação** de atendimento
- **Ligação de voz (Wavoip) + histórico de chamadas**
- **Transcrição de áudio recebido**
- **LGPD** (consentimento, ocultar número)
- **Backup em nuvem** (sobrevive à perda do número)
- **Relatórios + exportação Excel/PDF**, **exportar conversa em PDF**
- **Faturamento/assinaturas embutido** (Invoices, Subscriptions, gateways)
- **Aniversários, notas e motivos de finalização de ticket**

---

# 3. CONFIGURAÇÃO DOS PLANOS NO SISTEMA (o mapa exato)

O sistema parametriza cada plano pelo modelo **`Plan`** (`backend/src/models/Plan.ts`). São estes os campos que o admin configura por plano:

**Limites numéricos:** `users`, `connections` (nº de conexões WhatsApp), `queues` (nº de filas), `amount` (preço), `trialDays`, `recurrence`.
**Flags liga/desliga (feature gating):** `useWhatsapp`, `useFacebook`, `useInstagram`, `useCampaigns`, `useSchedules`, `useInternalChat`, `useExternalApi`, `useKanban`, `useOpenAi`, `useIntegrations`, `useWhatsappOfficial`, `wavoip`, `trial`, `isPublic`.

> ⚠️ **Não existe campo de "créditos de IA" no modelo.** `useOpenAi` é só on/off. Se for vender créditos, é desenvolvimento novo (ver §3 do doc de precificação).

## 3.1. Tabela de configuração — copie isto para o admin

> ⚠️ **CORRIGIDO pela reunião 06/06 (transcrição):** os 3 planos são **€47 / €97 / €147** (topo é 147, NÃO 197). Diferenciados por nº de usuários e canais. Valores R$/US$ abaixo são propostos — **confirmar com o Fred** (na reunião apareceu "R$147/mês" como mensalidade BR do topo no exemplo da empresa de cosméticos).

| Campo (sistema) | **START** €47 | **PRO** €97 | **BUSINESS** €147 |
|---|:---:|:---:|:---:|
| `users` | **3** *(confirmar)* | **5** *(confirmar)* | **10** *(confirmar)* |
| `connections` (conexões WhatsApp) | **1** | **2** | **3** |
| `queues` (filas) — *sugestão* | **2** | **5** | **15** |
| `amount` (€ / R$ / US$) | 47 / *a confirmar* / 37 | 97 / *a confirmar* / 77 | 147 / *a confirmar* / 117 |
| `recurrence` | mensal | mensal | mensal |
| `trialDays` | 7 | 7 | 7 |
| `isPublic` | ✅ true | ✅ true | ✅ true |
| `useWhatsapp` | ✅ | ✅ | ✅ |
| `useKanban` | ✅ | ✅ | ✅ |
| `useSchedules` (agendamento) | ✅ | ✅ | ✅ |
| `useInternalChat` (chat interno) | ✅ | ✅ | ✅ |
| `useInstagram` | ❌ | ✅ ⚠️ *decisão* | ✅ |
| `useFacebook` | ❌ | ✅ ⚠️ *decisão* | ✅ |
| `useCampaigns` (disparo) | ❌ | ✅ | ✅ |
| `useIntegrations` (Typebot/n8n/Dialogflow) | ❌ | ✅ | ✅ |
| `useOpenAi` (IA) | ❌ | ✅ ⚠️ *ver nota IA* | ✅ |
| `useExternalApi` (API aberta) | ❌ | ❌ | ✅ |
| `useWhatsappOfficial` (API oficial Meta) | ❌ | ❌ ⚠️ *decisão* | ✅ ⚠️ *decisão* |
| `wavoip` (ligação WhatsApp/AVOIP) | ❌ | ❌ | ✅ (add-on por usuário) |

Legenda: ✅ liga · ❌ desliga · ⚠️ ponto que precisa de decisão do Fred (ver §3.2).

## 3.2. Decisões pendentes do Fred (antes de fechar a config)

1. **Instagram + Facebook entram já no Pro ou só no Business?** A página vende omnichannel (WA+IG+FB) como recurso de destaque. Recomendo liberar no Pro pra reforçar a promessa. (acima deixei Pro = ✅).
2. **Agente de IA = produto separado com CRÉDITOS, NÃO recurso incluído no plano (confirmado na reunião 06/06).** O Fred foi explícito: "vamos vender o agente de IA com créditos, não vai ser dentro da mensalidade". O agente só é **desbloqueado no plano top (€147)** — quem não está nele não acessa. O cliente leigo não gera a própria API key da OpenAI; o INFIZAP gerencia e cobra crédito. Implicação técnica:
   - No sistema atual `useOpenAi` é só on/off — **liga só no Business (€147)**.
   - O **medidor de créditos não existe** e precisa ser construído para faturar o agente. Até lá, ou se vende o agente como add-on manual (deal a deal), ou se prioriza o dev dos créditos.
   - Na página: o card de €147 deve dizer **"desbloqueia o Agente de IA (créditos à parte)"**, não "agente de IA incluído".
3. **API Oficial Meta + Coexistência (`useWhatsappOfficial`):** confirmado na reunião como tecnologia central — o time vira **tech provider da Meta** (Thiago desenvolve). Exige o microserviço `api_oficial` no ar + conta Meta Business. Decidir se entra no €147 ou como add-on/Scale (deixei no €147). **Atenção de marketing:** o argumento "bloqueio em massa a partir de agosto" é **informação interna/de venda (SDR/comercial), NÃO banner público** (decisão do Fred). O selo "API oficial do WhatsApp / Meta" pode aparecer na página; o discurso anti-bloqueio fica para o time comercial.
4. **AVOIP/Wavoip:** add-on por usuário. No modelo `Plan` é só a flag `wavoip`. A cobrança por usuário precisa de tratamento à parte (não há campo de preço de add-on no Plan).
5. **Add-ons confirmados na reunião:** o cliente pode adicionar **+canais** (paga por canal) e **+usuários** (paga por usuário). Precisa existir no checkout.

## 3.3. Plano "Sob medida" (4º card) + esteira de implementação (CORRIGIDO pela reunião)

Não é um plano self-serve. É **venda assistida** (SDR qualifica → comercial → time de implementação). Valores ditos na reunião 06/06:

| Produto | Preço (reunião) | O que é |
|---|---|---|
| **Implementação guiada** | **€497** | Matheus desenha junto com o cliente: etapas do CRM, etiquetas, canais, scripts de atendimento, mensagens de boas-vindas/preço/follow-up. Cliente preenche formulário (15-20 perguntas) → entrega pré-configurada. 1º upsell. |
| **Implementação completa (done-for-you) + Agente de IA** | **€1.497 / R$1.497** | A equipe configura tudo + entrega 1 agente de IA (SDR/secretária: agenda, orçamento, remarca, confirma). Requer estar no plano €147. |

No sistema: criar Plan com `isPublic: false` para o "Sob medida", ou tratar fora do self-serve. Implementação é cobrança avulsa (one-time), não mensalidade.

## 3.4. Trial / freemium (confirmado na reunião)
- **7 dias grátis** para todos (cartão na frente → cobra no 8º dia).
- **Clientes próprios / beta:** cupom de **14 dias** em vez de 7.
- Lançamento: libera primeiro **grátis** para a base de clientes, depois começa a cobrar (estratégia MVP "valida manual, depois automatiza").

---

# 4. AÇÕES PARA O DEV — checklist

### Na PÁGINA (infizap.vercel.app)
- [ ] **Seção "Integrações nativas":** exibir só o conjunto voltado ao cliente — Meta (WhatsApp/IG/FB), OpenAI, Gemini, Dialogflow, Typebot, n8n, Cal.com, Webhook/API. Remover qualquer logo de gateway de pagamento e infra dessa barra.
- [ ] Remover/ajustar qualquer menção a Whisper, Pagar.me ou Chatwoot como "nativo" (não confirmados — ver §1).
- [ ] Alinhar o texto de IA dos planos à decisão do §3.2.2 (créditos vs on/off).
- [ ] Manter "transcrição de ligações" como roadmap jul/2026, mas pode-se citar "transcrição de áudios recebidos" como recurso atual.
- [ ] Confirmar valores dos 3 planos batem com a tabela §3.1 (€/R$/US$).

### No SISTEMA (admin de planos)
- [ ] Criar/editar os 3 planos com os campos exatos da tabela §3.1.
- [ ] Definir `queues` por plano (sugestão: 2/5/15 — confirmar com Fred).
- [ ] Configurar trial de 7 dias com cartão na frente (cobra no 8º dia).
- [ ] Decidir e aplicar as 4 decisões do §3.2.

### SEGURANÇA (urgente — achado na investigação do código)
- [ ] ⛔ O `README.md` raiz do código expõe **token do GitHub (`ghp_...`)**, secrets JWT no `.env.example` e senhas de admin do `api_oficial`. **Revogar/rotacionar essas credenciais imediatamente** e remover do repositório antes de qualquer deploy público.

---

> Dúvidas técnicas sobre o código: o sistema é um white-label da família Whaticket (backend Baileys em Sequelize/Postgres + microserviço NestJS/Prisma para API oficial + microserviço Python de transcrição + frontend React). Os limites globais da instância estão em `backend/.env.example` (`USER_LIMIT`, `CONNECTIONS_LIMIT`).
