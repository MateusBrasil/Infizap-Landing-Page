"""Inject universal lead capture + Stripe email prefill interceptor."""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

p = Path('infizap-lp-v1.html')
c = p.read_text(encoding='utf-8')

# ---------------------------------------------------------------------------
# Part A: mirror sessionStorage write in lead-form's handleSubmit to also
#         write localStorage. Find the existing try/sessionStorage.setItem
#         block in the form handler and add a localStorage twin right after.
# ---------------------------------------------------------------------------
old_persist = "try { sessionStorage.setItem('infizap_lead', JSON.stringify(lead)); } catch(_){}"
new_persist = "try { sessionStorage.setItem('infizap_lead', JSON.stringify(lead)); } catch(_){}\n    try { localStorage.setItem('infizap_lead', JSON.stringify(lead)); } catch(_){}"
n = c.count(old_persist)
print(f'lead-form persist line: {n} occurrence(s)')
if n == 1:
    c = c.replace(old_persist, new_persist)
    print('  → mirrored to localStorage')

# ---------------------------------------------------------------------------
# Part B: Inject the universal capture + Stripe interceptor script
# ---------------------------------------------------------------------------
NEW_SCRIPT = r"""
<script>
(function(){
  'use strict';

  var STORAGE_KEY = 'infizap_lead';
  var LEAD_ID_KEY = 'infizap_lead_id';
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  var DEBUG = (function(){
    try {
      var h = window.location.hostname || '';
      return h === 'localhost' || h === '127.0.0.1' || h.indexOf('vercel.app') !== -1;
    } catch(_){ return false; }
  })();
  function log(){ if (DEBUG && window.console) console.log.apply(console, ['[infizap-lead]'].concat([].slice.call(arguments))); }

  // ── Lead store: merge non-destructive ─────────────────────────────────────
  function readLead(){
    try {
      var ls = localStorage.getItem(STORAGE_KEY);
      if (ls) return JSON.parse(ls);
    } catch(_){}
    try {
      var ss = sessionStorage.getItem(STORAGE_KEY);
      if (ss) return JSON.parse(ss);
    } catch(_){}
    return {};
  }
  function writeLead(lead){
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(lead)); } catch(_){}
    try { sessionStorage.setItem(STORAGE_KEY, JSON.stringify(lead)); } catch(_){}
    try { window.__INFIZAP_LEAD = lead; } catch(_){}
  }
  function mergeIntoLead(patch){
    var cur = readLead();
    var next = Object.assign({}, cur);
    Object.keys(patch).forEach(function(k){
      var v = patch[k];
      if (v === undefined || v === null) return;
      if (typeof v === 'string' && v.trim() === '') return;
      next[k] = v;
    });
    next.updated_at = new Date().toISOString();
    // Also persist UTMs if they exist in fc_utms (set elsewhere)
    try {
      var utms = JSON.parse(sessionStorage.getItem('fc_utms') || '{}');
      if (Object.keys(utms).length) next.utms = utms;
    } catch(_){}
    // Country dial code from the picker if available
    try {
      var dialEl = document.getElementById('cp-country-code');
      if (dialEl && dialEl.textContent && dialEl.textContent.trim()) next.country_dial = dialEl.textContent.trim();
    } catch(_){}
    writeLead(next);
    return next;
  }

  // ── Lead anonymous ID (for Stripe client_reference_id) ─────────────────────
  function getOrCreateLeadId(){
    try {
      var id = localStorage.getItem(LEAD_ID_KEY);
      if (id) return id;
    } catch(_){}
    var rnd;
    try {
      if (window.crypto && crypto.randomUUID) rnd = crypto.randomUUID().replace(/-/g, '').slice(0, 16);
    } catch(_){}
    if (!rnd) rnd = Math.random().toString(36).slice(2, 12) + Date.now().toString(36).slice(-6);
    var id = 'anon_' + rnd;
    try { localStorage.setItem(LEAD_ID_KEY, id); } catch(_){}
    return id;
  }

  // ── Field classifier ─────────────────────────────────────────────────────
  function classifyField(el){
    if (!el || el.tagName !== 'INPUT') return null;
    var t = (el.type || '').toLowerCase();
    var id = (el.id || '').toLowerCase();
    var ph = (el.placeholder || '').toLowerCase();
    var name = (el.name || '').toLowerCase();
    // email
    if (t === 'email' || /email|correo|mail/.test(id) || /email|correo|@/.test(ph) || /email|mail/.test(name)) return 'email';
    // phone
    if (t === 'tel' || /phone|tel|whatsapp|telefone/.test(id) || /phone|tel|whatsapp|telefone|número de/.test(ph)) return 'phone';
    // name (do NOT match "company name", "business name" by default — keep it specific to user name fields)
    if (/(^|[-_])(name|nome)([-_]|$)/.test(id) || /(seu nome|tu nombre|your name|complete name|nome completo)/i.test(ph)) return 'name';
    // fallback: if id/placeholder contains generic "nome"/"name"
    if (/nome|name/.test(id) || /nome|name/.test(ph)) return 'name';
    return null;
  }

  // ── Passive capture: any input → mergeIntoLead ───────────────────────────
  function onInput(e){
    var el = e.target;
    var kind = classifyField(el);
    if (!kind) return;
    var v = (el.value || '').trim();
    if (!v) return;
    if (kind === 'email' && !EMAIL_RE.test(v)) return; // wait until it's a valid-looking email
    var patch = {}; patch[kind] = v;
    var lead = mergeIntoLead(patch);
    log('captured', kind + '=' + v.slice(0, 40), '→', { email: lead.email, name: lead.name, phone: lead.phone });
  }
  document.addEventListener('input', onInput, true);
  document.addEventListener('change', onInput, true);
  document.addEventListener('blur', onInput, true);

  // ── Stripe URL enrichment ────────────────────────────────────────────────
  function enrichStripeUrl(href){
    var lead = readLead();
    if (!lead || !lead.email || !EMAIL_RE.test(lead.email)) return href;
    try {
      var u = new URL(href);
      u.searchParams.set('prefilled_email', lead.email);
      u.searchParams.set('client_reference_id', getOrCreateLeadId());
      // Forward UTMs as standard tracking params on Stripe (no-op but preserved if Stripe ever surfaces them)
      if (lead.utms && typeof lead.utms === 'object') {
        ['utm_source','utm_medium','utm_campaign','utm_term','utm_content'].forEach(function(k){
          if (lead.utms[k] && !u.searchParams.get(k)) u.searchParams.set(k, lead.utms[k]);
        });
      }
      return u.toString();
    } catch(_){
      return href;
    }
  }

  // ── Click interceptor on Stripe Payment Link anchors ─────────────────────
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
  }, true);

  // ── On boot: scan existing inputs once (in case modal is pre-populated) ──
  try {
    var inputs = document.querySelectorAll('input');
    for (var i = 0; i < inputs.length; i++) {
      onInput({ target: inputs[i] });
    }
  } catch(_){}

  log('lead capture + Stripe enrich ready');
})();
</script>
"""

# Inject just before </body>
body_end = c.rfind('</body>')
if body_end < 0:
    print('ERROR: </body> not found'); sys.exit(1)
c = c[:body_end] + NEW_SCRIPT + c[body_end:]

p.write_text(c, encoding='utf-8')
print(f'\nfile size: {len(c)}')
print(f'script injected ({len(NEW_SCRIPT)} chars)')
