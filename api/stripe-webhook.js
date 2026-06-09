// api/stripe-webhook.js
//
// Vercel Serverless Function (site HTML estatico + funcoes em /api).
// Webhook da Stripe -> provisionamento automatico no INFIZAP.
//
// Fluxo:
//   Cliente paga (Stripe Payment Link)
//     -> Stripe envia checkout.session.completed pra esta funcao
//     -> validamos a assinatura
//     -> descobrimos o plano comprado (price ID)
//     -> logamos como admin no infizap
//     -> criamos a empresa do cliente com o plano certo
//
// Importante: o gatilho e o WEBHOOK (servidor), nao a pagina /obrigado.
// Assim a empresa e criada mesmo que o cliente feche a aba apos pagar.

const Stripe = require("stripe");
const nodemailer = require("nodemailer");

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
const API_BASE = process.env.INFIZAP_API_BASE || "https://appbk.infizap.com";

// =====================================================================
//  MAPA DE PLANOS  ->  SO FALTA O planId DO INFIZAP
// =====================================================================
// Mapeamos pelo VALOR pago (amount_total em centavos) + moeda. Vantagem:
// funciona direto com seus Payment Links atuais, sem precisar de price IDs.
// Cada plano/recorrencia tem um valor unico, entao da pra distinguir todos.
//
// FALTA: depois de criar Start/Pro/Business no painel infizap, troque os
// planId: 0 pelo id real de cada plano. Pra listar os ids, rode no console
// do navegador (logado no painel):
//   fetch("https://appbk.infizap.com/plans/list",{headers:{Authorization:"Bearer "+JSON.parse(localStorage.getItem("token"))}}).then(r=>r.json()).then(console.table)
//
// Referencia dos Payment Links (so pra conferencia; o webhook usa o valor):
//   Start Mensal     47,00  -> buy.stripe.com/6oU28q7nrcx61AjfzK9R60w
//   Start Anual     470,00  -> buy.stripe.com/3cI8wOdLP8gQ92Lcny9R60z
//   Pro Mensal       97,00  -> buy.stripe.com/4gM4gy8rv7cM4Mvcny9R60x
//   Pro Anual       970,00  -> buy.stripe.com/dRm4gygY18gQ0wf1IU9R60A
//   Business Mensal 197,00  -> buy.stripe.com/aFa8wO7nr9kU3Ir9bm9R60y
//   Business Anual 1970,00  -> buy.stripe.com/cNi5kCbDHdBaceX5Za9R60B
const PLAN_BY_AMOUNT = {
  // Mensais (planId 4/5/6)        |  Anuais (planId 7/8/9)
  "eur:4700":   { label: "Start Mensal",    planId: 4, recurrence: "MENSAL" },
  "eur:47000":  { label: "Start Anual",     planId: 7, recurrence: "ANUAL"  },
  "eur:9700":   { label: "Pro Mensal",      planId: 5, recurrence: "MENSAL" },
  "eur:97000":  { label: "Pro Anual",       planId: 8, recurrence: "ANUAL"  },
  "eur:19700":  { label: "Business Mensal", planId: 6, recurrence: "MENSAL" },
  "eur:147000": { label: "Business Anual",  planId: 9, recurrence: "ANUAL"  }, // novo preco €1470
  "eur:197000": { label: "Business Anual (preco antigo)", planId: 9, recurrence: "ANUAL" }, // alias seguranca
};

// (Opcional, mais robusto) Se um dia usar CUPONS de desconto, o valor pago muda
// e o mapa por valor erra. Nesse caso preencha aqui o mapa por Price ID
// (Stripe > Produtos > plano > preco price_...). Tem prioridade quando casar.
const PLAN_BY_PRICE = {
  // "price_xxx": { label: "Start Mensal", planId: 0, recurrence: "MENSAL" },
};

function resolvePlan(session, li) {
  li = li || {};
  // 1) por Price ID (mais preciso) se voce preencheu PLAN_BY_PRICE
  if (li.priceId && PLAN_BY_PRICE[li.priceId]) return PLAN_BY_PRICE[li.priceId];
  // 2) pelo preco unitario do plano (nao muda com imposto nem desconto)
  if (li.unitAmount != null) {
    const k = `${(li.unitCurrency || session.currency || "").toLowerCase()}:${li.unitAmount}`;
    if (PLAN_BY_AMOUNT[k]) return PLAN_BY_AMOUNT[k];
  }
  // 3) fallback: total pago (so funciona sem imposto/desconto)
  const key = `${(session.currency || "").toLowerCase()}:${session.amount_total}`;
  return PLAN_BY_AMOUNT[key] || null;
}

// Vercel/Stripe: precisamos do corpo CRU pra validar a assinatura.
module.exports.config = { api: { bodyParser: false } };

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).send("Method Not Allowed");
  }

  let event;
  try {
    const rawBody = await readRawBody(req);
    const sig = req.headers["stripe-signature"];
    event = stripe.webhooks.constructEvent(
      rawBody,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    console.error("[infizap] assinatura invalida:", err.message);
    return res.status(400).send(`Webhook signature error: ${err.message}`);
  }

  if (event.type !== "checkout.session.completed") {
    return res.status(200).json({ received: true, ignored: event.type });
  }

  try {
    await provisionFromSession(event.data.object);
    return res.status(200).json({ received: true, provisioned: true });
  } catch (err) {
    // Logamos mas devolvemos 200 pra Stripe nao reenviar em loop em erro permanente.
    // Pra reprocessar manualmente, use "Resend" no painel da Stripe.
    console.error("[infizap] falha ao provisionar:", err && err.message);
    return res
      .status(200)
      .json({ received: true, provisioned: false, error: String(err && err.message) });
  }
};

async function provisionFromSession(session) {
  // 1) Dados do cliente (vem do Checkout/Payment Link da Stripe)
  const email =
    (session.customer_details && session.customer_details.email) ||
    session.customer_email;
  const name =
    (session.customer_details && session.customer_details.name) ||
    (email ? email.split("@")[0] : "Cliente INFIZAP");
  const phone =
    (session.customer_details && session.customer_details.phone) || "";

  if (!email) throw new Error("Sessao sem email do cliente");

  // 2) Qual plano foi comprado? Resolve pelo PRECO DO PLANO na linha do pedido
  //    (unit_amount / price.id) — estavel mesmo com imposto (VAT) ou desconto.
  //    Cai pro amount_total so se nao conseguir as line items.
  let li = {};
  try {
    const lineItems = await stripe.checkout.sessions.listLineItems(session.id, {
      limit: 1,
    });
    const item = lineItems.data[0];
    if (item && item.price) {
      li.priceId = item.price.id || null;
      li.unitAmount = item.price.unit_amount != null ? item.price.unit_amount : null;
      li.unitCurrency = item.price.currency || null;
    }
  } catch (_) {
    // segue so com o valor pago (amount_total)
  }

  const mapped = resolvePlan(session, li);
  if (!mapped) {
    throw new Error(
      `Plano nao reconhecido. currency=${session.currency} amount_total=${session.amount_total} priceId=${priceId}`
    );
  }
  if (!mapped.planId) {
    throw new Error(
      `planId nao configurado para "${mapped.label}". Edite PLAN_BY_AMOUNT em api/stripe-webhook.js`
    );
  }

  // 3) Login admin no infizap -> token JWT
  const token = await infizapLogin();

  // 4) Idempotencia: nao duplica se ja existe empresa com esse email
  const existing = await findCompanyByEmail(token, email);
  if (existing) {
    console.log(`[infizap] empresa ja existe para ${email} (id ${existing.id}). Pulando.`);
    return;
  }

  // 5) Senha inicial do cliente (ele loga com email + esta senha)
  const password = generatePassword();

  // 6) Cria a empresa + seta o plano
  const company = await createCompany(token, {
    name,
    email,
    phone,
    password,
    planId: mapped.planId,
    recurrence: mapped.recurrence,
    dueDate: computeDueDate(mapped.recurrence),
  });

  console.log(
    `[infizap] empresa criada: id=${company.id} email=${email} planId=${mapped.planId} ref=${session.client_reference_id || "-"}`
  );

  // 7) Email de boas-vindas com as credenciais, no IDIOMA da compra.
  //    O idioma vem carimbado no client_reference_id pela landing (__l_pt/en/es/ar).
  //    NUNCA derruba a criacao da empresa: se o email falhar, so logamos.
  const lang = parseLang(session.client_reference_id);
  try {
    await sendWelcomeEmail({ email, name, password, planLabel: mapped.label, lang });
    console.log(`[infizap] email de boas-vindas (${lang}) enviado para ${email}`);
  } catch (e) {
    console.error("[infizap] falha ao enviar email de boas-vindas:", e && e.message);
  }
}

// ───────────────────────── EMAIL DE BOAS-VINDAS ─────────────────────────
// Envia via SMTP (ex.: caixa do Hostinger no-reply@infizap.com), no idioma
// da compra (pt/en/es/ar). Arabe (ar) e renderizado da direita pra esquerda.
// Variaveis na Vercel: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, MAIL_FROM,
// e opcional APP_LOGIN_URL (default https://app.infizap.com/login).

// Textos do email por idioma (pt = padrao).
const EMAIL_T = {
  pt: {
    subject: "Bem-vindo ao INFIZAP — seu acesso está pronto 🎉",
    hi: "Olá",
    intro: (p) => `Seu pagamento do <strong>${p}</strong> foi aprovado e sua conta já está pronta. Use os dados abaixo para entrar:`,
    access: "Acesso", emailLabel: "Email", tempPass: "Senha temporária",
    security: 'Por segurança, <strong>troque a senha no primeiro acesso</strong> (no menu do seu perfil dentro da plataforma). Se esquecer a senha, use a opção "Esqueci minha senha" na tela de login.',
    button: "Entrar na plataforma",
    help: "Precisa de ajuda? Responda este email.", team: "— Equipe INFIZAP",
    textIntro: (p) => `Seu pagamento do ${p} foi aprovado e sua conta está pronta.`,
    textSecurity: 'Troque a senha no primeiro acesso. Se esquecer, use "Esqueci minha senha" no login.',
  },
  en: {
    subject: "Welcome to INFIZAP — your access is ready 🎉",
    hi: "Hi",
    intro: (p) => `Your payment for <strong>${p}</strong> was approved and your account is ready. Use the details below to log in:`,
    access: "Login URL", emailLabel: "Email", tempPass: "Temporary password",
    security: 'For security, <strong>change your password on first login</strong> (in your profile menu inside the platform). If you forget it, use the "Forgot password" option on the login screen.',
    button: "Log in to the platform",
    help: "Need help? Just reply to this email.", team: "— The INFIZAP Team",
    textIntro: (p) => `Your payment for ${p} was approved and your account is ready.`,
    textSecurity: 'Change your password on first login. If you forget it, use "Forgot password" on the login screen.',
  },
  es: {
    subject: "Bienvenido a INFIZAP — tu acceso está listo 🎉",
    hi: "Hola",
    intro: (p) => `Tu pago del <strong>${p}</strong> fue aprobado y tu cuenta ya está lista. Usa los datos de abajo para entrar:`,
    access: "Acceso", emailLabel: "Email", tempPass: "Contraseña temporal",
    security: 'Por seguridad, <strong>cambia la contraseña en el primer acceso</strong> (en el menú de tu perfil dentro de la plataforma). Si la olvidas, usa la opción "Olvidé mi contraseña" en la pantalla de inicio de sesión.',
    button: "Entrar a la plataforma",
    help: "¿Necesitas ayuda? Responde a este correo.", team: "— Equipo INFIZAP",
    textIntro: (p) => `Tu pago del ${p} fue aprobado y tu cuenta está lista.`,
    textSecurity: 'Cambia la contraseña en el primer acceso. Si la olvidas, usa "Olvidé mi contraseña" en el login.',
  },
  ar: {
    subject: "مرحبًا بك في INFIZAP — حسابك جاهز 🎉",
    hi: "مرحبًا",
    intro: (p) => `تمت الموافقة على دفعتك لـ <strong>${p}</strong> وحسابك جاهز الآن. استخدم البيانات أدناه لتسجيل الدخول:`,
    access: "رابط الدخول", emailLabel: "البريد الإلكتروني", tempPass: "كلمة مرور مؤقتة",
    security: 'لأمانك، <strong>قم بتغيير كلمة المرور عند أول تسجيل دخول</strong> (من قائمة ملفك الشخصي داخل المنصة). إذا نسيتها، استخدم خيار "نسيت كلمة المرور" في شاشة تسجيل الدخول.',
    button: "تسجيل الدخول إلى المنصة",
    help: "هل تحتاج إلى مساعدة؟ فقط رد على هذا البريد.", team: "— فريق INFIZAP",
    textIntro: (p) => `تمت الموافقة على دفعتك لـ ${p} وحسابك جاهز.`,
    textSecurity: 'قم بتغيير كلمة المرور عند أول تسجيل دخول. إذا نسيتها، استخدم "نسيت كلمة المرور" في تسجيل الدخول.',
  },
};

// Le o idioma carimbado no client_reference_id (ex.: anon_xxx__l_en) -> "en".
// Se nao vier idioma, o padrao e INGLES (alcanca mais gente).
function parseLang(ref) {
  const m = /__l_(pt|en|es|ar)\b/.exec(ref || "");
  return m ? m[1] : "en";
}

async function sendWelcomeEmail({ email, name, password, planLabel, lang }) {
  if (!process.env.SMTP_HOST) {
    throw new Error("SMTP nao configurado (defina SMTP_HOST/PORT/USER/PASS)");
  }
  const t = EMAIL_T[lang] || EMAIL_T.en;
  const dir = lang === "ar" ? "rtl" : "ltr";
  const align = lang === "ar" ? "right" : "left";

  const port = Number(process.env.SMTP_PORT || 465);
  const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port,
    secure: port === 465, // 465 = SSL; 587 = STARTTLS
    auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
  });

  const loginUrl = process.env.APP_LOGIN_URL || "https://app.infizap.com/login";
  const from = process.env.MAIL_FROM || "INFIZAP <no-reply@infizap.com>";
  const firstName = (name || "").split(" ")[0] || t.hi;

  const planSafe = escapeHtml(planLabel || "INFIZAP");
  const html = `
  <div dir="${dir}" style="font-family:Arial,Helvetica,sans-serif;max-width:560px;margin:0 auto;color:#0f172a;text-align:${align}">
    <div style="background:#0f766e;padding:24px;border-radius:12px 12px 0 0;text-align:center">
      <span style="color:#fff;font-size:22px;font-weight:700;letter-spacing:1px">INFIZAP</span>
    </div>
    <div style="border:1px solid #e2e8f0;border-top:0;border-radius:0 0 12px 12px;padding:28px">
      <p style="font-size:16px">${t.hi}, ${escapeHtml(firstName)} 👋</p>
      <p style="font-size:15px;line-height:1.6">${t.intro(planSafe)}</p>
      <div style="background:#f1f5f9;border-radius:10px;padding:18px;margin:18px 0;font-size:15px">
        <div style="margin-bottom:8px"><strong>${t.access}:</strong>
          <a href="${loginUrl}" style="color:#0f766e">${loginUrl}</a></div>
        <div style="margin-bottom:8px"><strong>${t.emailLabel}:</strong> ${escapeHtml(email)}</div>
        <div><strong>${t.tempPass}:</strong>
          <code style="background:#fff;padding:2px 8px;border-radius:6px;border:1px solid #cbd5e1">${escapeHtml(password)}</code></div>
      </div>
      <p style="font-size:14px;line-height:1.6;color:#475569">${t.security}</p>
      <div style="text-align:center;margin:24px 0">
        <a href="${loginUrl}" style="background:#0f766e;color:#fff;text-decoration:none;padding:12px 28px;border-radius:8px;font-weight:600;display:inline-block">${t.button}</a>
      </div>
      <p style="font-size:13px;color:#94a3b8">${t.help} ${t.team}</p>
    </div>
  </div>`;

  const text =
    `${t.hi}, ${firstName}!\n\n` +
    `${t.textIntro(planLabel || "INFIZAP")}\n\n` +
    `${t.access}: ${loginUrl}\n${t.emailLabel}: ${email}\n${t.tempPass}: ${password}\n\n` +
    `${t.textSecurity}\n\n${t.team}`;

  await transporter.sendMail({
    from,
    to: email,
    subject: t.subject,
    text,
    html,
  });
}

function escapeHtml(s) {
  return String(s || "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );
}

// ───────────────────────── INFIZAP API ─────────────────────────
async function infizapLogin() {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: process.env.INFIZAP_ADMIN_EMAIL,
      password: process.env.INFIZAP_ADMIN_PASSWORD,
    }),
  });
  if (!res.ok) {
    const t = await res.text();
    throw new Error(`Login infizap falhou (${res.status}): ${t.slice(0, 200)}`);
  }
  const data = await res.json();
  if (!data.token) throw new Error("Login infizap nao retornou token");
  return data.token;
}

async function findCompanyByEmail(token, email) {
  const res = await fetch(`${API_BASE}/companies/list`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`GET /companies/list falhou (${res.status})`);
  const list = await res.json();
  return (
    list.find((c) => (c.email || "").toLowerCase() === email.toLowerCase()) ||
    null
  );
}

async function createCompany(token, input) {
  const res = await fetch(`${API_BASE}/companies`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name: input.name,
      email: input.email,
      phone: input.phone,
      password: input.password,
      planId: input.planId,
      status: true,
      campaignsEnabled: true,
      dueDate: input.dueDate,
      recurrence: input.recurrence,
    }),
  });
  if (!res.ok) {
    const t = await res.text();
    throw new Error(`POST /companies falhou (${res.status}): ${t.slice(0, 300)}`);
  }
  return res.json();
}

// ───────────────────────── helpers ─────────────────────────
function computeDueDate(recurrence) {
  const d = new Date();
  d.setDate(d.getDate() + (recurrence === "ANUAL" ? 365 : 30));
  return d.toISOString().slice(0, 10); // YYYY-MM-DD
}

function generatePassword() {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789";
  let out = "";
  for (let i = 0; i < 12; i++)
    out += chars[Math.floor(Math.random() * chars.length)];
  return out;
}

function readRawBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on("data", (c) => chunks.push(typeof c === "string" ? Buffer.from(c) : c));
    req.on("end", () => resolve(Buffer.concat(chunks)));
    req.on("error", reject);
  });
}
