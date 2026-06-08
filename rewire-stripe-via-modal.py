"""Rewire: click on pricing CTA → open lead modal → on submit → Stripe URL for that plan."""
import sys, re
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

p = Path('infizap-lp-v1.html')
c = p.read_text(encoding='utf-8')

# ---------------------------------------------------------------------------
# EDIT 1: change handleSubmit to read pending Stripe URL from sessionStorage
# before using STRIPE_CHECKOUT_URL placeholder.
# ---------------------------------------------------------------------------
old_redirect = """    // Redirect to Stripe checkout (with optional prefilled email)
    var url = STRIPE_CHECKOUT_URL;
    if (url.indexOf('PLACEHOLDER') !== -1){
      // No real Stripe link yet — go straight to obrigado.html for preview
      window.location.href = '/obrigado.html';
      return;
    }
    // Prefill email on the Stripe checkout
    try {
      var u = new URL(url);
      u.searchParams.set('prefilled_email', email);
      url = u.toString();
    } catch(_){}
    window.location.href = url;"""

new_redirect = """    // Plan-specific Stripe URL set when user clicked a pricing card; else fall back
    var pendingUrl = '';
    try { pendingUrl = sessionStorage.getItem('infizap_pending_stripe_url') || ''; } catch(_){}
    var url = pendingUrl || STRIPE_CHECKOUT_URL;
    // Consume the pending URL so a future submit doesn't reuse a stale plan
    try { sessionStorage.removeItem('infizap_pending_stripe_url'); } catch(_){}
    try { sessionStorage.removeItem('infizap_pending_stripe_plan'); } catch(_){}
    if (url.indexOf('PLACEHOLDER') !== -1){
      // No real Stripe link yet — go straight to obrigado.html for preview
      window.location.href = '/obrigado.html';
      return;
    }
    // Prefill email + reference id on the Stripe checkout
    try {
      var u = new URL(url);
      u.searchParams.set('prefilled_email', email);
      var leadId = (function(){
        try { var v = localStorage.getItem('infizap_lead_id'); if (v) return v;
              var rnd = (window.crypto && crypto.randomUUID) ? crypto.randomUUID().replace(/-/g,'').slice(0,16) : (Math.random().toString(36).slice(2,12)+Date.now().toString(36).slice(-6));
              var nid = 'anon_' + rnd; localStorage.setItem('infizap_lead_id', nid); return nid;
        } catch(_){ return ''; }
      })();
      if (leadId) u.searchParams.set('client_reference_id', leadId);
      url = u.toString();
    } catch(_){}
    window.location.href = url;"""

if old_redirect in c:
    c = c.replace(old_redirect, new_redirect)
    print('handleSubmit redirect block patched')
else:
    print('ERROR: handleSubmit redirect block not found')
    sys.exit(1)

# ---------------------------------------------------------------------------
# EDIT 2: Rewrite the Stripe click interceptor to OPEN MODAL instead of going
# straight to Stripe.
# ---------------------------------------------------------------------------
old_interceptor = """  // ── Click interceptor on Stripe Payment Link anchors ─────────────────────
  document.addEventListener('click', function(e){
    var a = e.target.closest && e.target.closest('a');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    if (href.indexOf('https://buy.stripe.com/') !== 0) return;
    var enriched = enrichStripeUrl(href);
    if (enriched === href) return; // nothing to add — let default navigation happen
    log('enriching Stripe URL:', enriched);
    // Respect modifier-clicks and target="_blank"
    var newTab = (a.target === '_blank') || e.metaKey || e.ctrlKey || e.shiftKey || e.button === 1;
    e.preventDefault();
    if (newTab) {
      window.open(enriched, '_blank', 'noopener,noreferrer');
    } else {
      window.location.assign(enriched);
    }
  }, true);"""

new_interceptor = """  // ── Helpers to open/close the lead modal and read which plan was clicked ──
  function getPlanFromAnchor(a){
    try {
      var card = a.closest('.pricing-card-content') || a.closest('.pricing-card-inner') || a.closest('[class*="pricing"]');
      if (!card) return '';
      var nameEl = card.querySelector('.pricing-plan-name');
      var periodEl = card.querySelector('.pricing-plan-period');
      var plan = nameEl ? nameEl.textContent.trim() : '';
      var period = periodEl ? periodEl.textContent.trim() : '';
      if (plan && period) return plan + ' · ' + period;
      return plan || period || '';
    } catch(_){ return ''; }
  }

  function prefillLeadModalFromStorage(){
    try {
      var lead = (function(){
        var ls = localStorage.getItem(STORAGE_KEY); if (ls) return JSON.parse(ls);
        var ss = sessionStorage.getItem(STORAGE_KEY); if (ss) return JSON.parse(ss);
        return {};
      })();
      if (!lead) return;
      var setIf = function(id, val){
        var el = document.getElementById(id);
        if (el && val && !el.value) el.value = val;
      };
      setIf('lead-name', lead.name);
      setIf('lead-email', lead.email);
      setIf('lead-phone', lead.phone);
    } catch(_){}
  }

  function showSelectedPlanLabel(planLabel){
    if (!planLabel) return;
    var step1 = document.getElementById('lead-step1');
    if (!step1) return;
    var existing = document.getElementById('lead-selected-plan');
    if (existing) { existing.querySelector('.label-value').textContent = planLabel; return; }
    var h2 = step1.querySelector('h2');
    if (!h2) return;
    var pill = document.createElement('div');
    pill.id = 'lead-selected-plan';
    pill.className = 'mt-1 mb-4 text-center';
    pill.innerHTML = '<span class="inline-flex items-center gap-1.5 rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-[11px] font-semibold text-primary"><svg viewBox="0 0 20 20" fill="currentColor" class="h-3 w-3" aria-hidden="true"><path d="M10 1l2.6 5.3 5.9.8-4.3 4.1 1 5.8L10 14.3l-5.2 2.7 1-5.8L1.5 7.1l5.9-.8L10 1z"/></svg>Plano selecionado: <span class="label-value">' + planLabel + '</span></span>';
    h2.parentNode.insertBefore(pill, h2.nextSibling);
  }

  function openLeadModal(planLabel){
    var overlay = document.getElementById('lead-overlay');
    var modal = document.getElementById('lead-modal');
    if (!overlay || !modal) return;
    overlay.style.display = 'block';
    modal.style.display = 'block';
    try { document.body.style.overflow = 'hidden'; } catch(_){}
    prefillLeadModalFromStorage();
    showSelectedPlanLabel(planLabel);
    // Focus first empty input for fast keyboard entry
    setTimeout(function(){
      var firstEmpty = ['lead-name','lead-phone','lead-email'].map(function(id){return document.getElementById(id);}).filter(function(el){return el && !el.value;})[0];
      if (firstEmpty) firstEmpty.focus();
    }, 60);
  }

  function closeLeadModal(){
    var overlay = document.getElementById('lead-overlay');
    var modal = document.getElementById('lead-modal');
    if (overlay) overlay.style.display = 'none';
    if (modal) modal.style.display = 'none';
    try { document.body.style.overflow = ''; } catch(_){}
    // Clear pending plan URL — user dismissed without submitting
    try { sessionStorage.removeItem('infizap_pending_stripe_url'); } catch(_){}
    try { sessionStorage.removeItem('infizap_pending_stripe_plan'); } catch(_){}
    var pill = document.getElementById('lead-selected-plan'); if (pill) pill.parentNode.removeChild(pill);
  }

  // Wire modal close interactions (X button, overlay click, Escape key)
  document.addEventListener('click', function(e){
    if (e.target.closest && e.target.closest('#lead-modal-close')) { e.preventDefault(); closeLeadModal(); return; }
    if (e.target.id === 'lead-overlay') { closeLeadModal(); return; }
  });
  document.addEventListener('keydown', function(e){
    if (e.key === 'Escape') {
      var m = document.getElementById('lead-modal');
      if (m && m.style.display !== 'none') closeLeadModal();
    }
  });

  // ── Click interceptor on Stripe Payment Link anchors ─────────────────────
  document.addEventListener('click', function(e){
    var a = e.target.closest && e.target.closest('a');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    if (href.indexOf('https://buy.stripe.com/') !== 0) return;
    // Modifier clicks: skip modal flow (let the browser handle Ctrl/middle-click new-tab as before)
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.button === 1) {
      var enriched = enrichStripeUrl(href);
      if (enriched !== href) {
        e.preventDefault();
        window.open(enriched, '_blank', 'noopener,noreferrer');
      }
      return;
    }
    // Standard click → store URL + open modal first
    e.preventDefault();
    e.stopPropagation();
    var planLabel = getPlanFromAnchor(a);
    try { sessionStorage.setItem('infizap_pending_stripe_url', href); } catch(_){}
    try { if (planLabel) sessionStorage.setItem('infizap_pending_stripe_plan', planLabel); } catch(_){}
    log('plan clicked → opening lead modal:', planLabel || '(unknown plan)', '→', href);
    openLeadModal(planLabel);
  }, true);"""

if old_interceptor in c:
    c = c.replace(old_interceptor, new_interceptor)
    print('Stripe click interceptor rewritten to open lead modal')
else:
    print('ERROR: old interceptor block not found')
    sys.exit(1)

p.write_text(c, encoding='utf-8')
print(f'\nfile size: {len(c)}')
