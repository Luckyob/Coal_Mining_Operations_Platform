/* MineCore interactivity layer.
   Runs in the browser only: it reads the existing /api/... endpoints and
   upgrades the server-rendered page. No Python changes needed beyond serving this file. */
(() => {
  'use strict';

  // ---------- helpers ----------
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const esc = (t) => String(t).replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const fmt = (n) => Number(n).toLocaleString('en-US');

  async function api(path) {
    const res = await fetch(path);
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
    return res.json();
  }

  const store = {
    get(key, fallback) {
      try { const v = JSON.parse(localStorage.getItem(key)); return v === null ? fallback : v; }
      catch { return fallback; }
    },
    set(key, value) {
      try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* storage blocked: ignore */ }
    },
  };

  // Hook for the Policy Explainer (RAG). Whoever builds it can set:
  //   MineCore.askPolicy = async (stage, outputEl) => { outputEl.textContent = '...answer...'; };
  // where stage = { id, name }. Until then the page shows the question it would ask.
  window.MineCore = window.MineCore || { askPolicy: null };

  // ---------- toasts ----------
  function toast(message) {
    let box = $('#mc-toasts');
    if (!box) {
      box = document.createElement('div');
      box.id = 'mc-toasts';
      document.body.appendChild(box);
    }
    const el = document.createElement('div');
    el.className = 'mc-toast';
    el.textContent = message;
    box.appendChild(el);
    setTimeout(() => el.remove(), 3200);
  }

  // ---------- site detail drawer ----------
  const backdrop = document.createElement('div');
  backdrop.id = 'mc-backdrop';
  const drawer = document.createElement('aside');
  drawer.id = 'mc-drawer';
  drawer.setAttribute('role', 'dialog');
  drawer.setAttribute('aria-label', 'Site details');
  drawer.setAttribute('aria-hidden', 'true');
  drawer.innerHTML = `
    <div class="mc-drawer-head">
      <div><h3 id="mc-drawer-title"></h3><small id="mc-drawer-sub"></small></div>
      <button id="mc-drawer-close" type="button" aria-label="Close panel">&times;</button>
    </div>
    <div id="mc-drawer-body"></div>`;
  document.body.append(backdrop, drawer);

  let lastFocus = null;
  function openDrawer() {
    lastFocus = document.activeElement;
    backdrop.classList.add('open');
    drawer.classList.add('open');
    drawer.setAttribute('aria-hidden', 'false');
    $('#mc-drawer-close').focus();
  }
  function closeDrawer() {
    backdrop.classList.remove('open');
    drawer.classList.remove('open');
    drawer.setAttribute('aria-hidden', 'true');
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  backdrop.addEventListener('click', closeDrawer);
  $('#mc-drawer-close').addEventListener('click', closeDrawer);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeDrawer(); });

  async function showSite(siteId) {
    $('#mc-drawer-title').textContent = 'Loading…';
    $('#mc-drawer-sub').textContent = '';
    $('#mc-drawer-body').innerHTML = '';
    openDrawer();
    try {
      const dash = await api(`/api/dashboard/${siteId}`);
      const safety = await api(`/api/mining/stages/${dash.operation.stage_id}/safety`);
      renderSite(dash, safety);
    } catch (err) {
      $('#mc-drawer-title').textContent = 'Could not load site';
      $('#mc-drawer-body').innerHTML = '<p class="mc-empty">Check that the server is running, then try again.</p>';
    }
  }

  function renderSite(d, safety) {
    const key = `mc-check-${d.site.id}-${safety.stage_id}`;
    const done = store.get(key, []);
    const total = safety.safety_requirements.length;

    const equipment = d.equipment.items.length
      ? d.equipment.items.map((e) =>
          `<div class="mc-row"><span>${esc(e.name)}</span><em>${esc(e.status)}</em></div>`).join('')
      : '<p class="mc-empty">No equipment assigned at this stage.</p>';

    const alertRows = d.alerts.length
      ? d.alerts.map((a) =>
          `<div class="mc-row"><span>${esc(a.message)}</span><em>${esc(a.severity)}</em></div>`).join('')
      : '<p class="mc-empty">No open alerts.</p>';

    const checks = safety.safety_requirements.map((r, i) =>
      `<label class="mc-check"><input type="checkbox" data-i="${i}" ${done.includes(i) ? 'checked' : ''}>
       <span>${esc(r)}</span></label>`).join('');

    $('#mc-drawer-title').textContent = d.site.name;
    $('#mc-drawer-sub').textContent = d.site.location;
    $('#mc-drawer-body').innerHTML = `
      <div class="mc-kpis">
        <div class="mc-kpi"><span>Current stage</span><strong>${esc(d.operation.current_stage)}</strong></div>
        <div class="mc-kpi"><span>Production today</span><strong>${fmt(d.production.production_today)} ${esc(d.production.unit)}</strong></div>
        <div class="mc-kpi"><span>Safety status</span><strong>${esc(d.safety.status)}</strong></div>
        <div class="mc-kpi"><span>Equipment operational</span><strong>${d.equipment.operational}/${d.equipment.total}</strong></div>
      </div>
      <h4>Safety checklist: ${esc(safety.stage)}</h4>
      <div class="mc-progress"><div id="mc-prog"></div></div>
      <small id="mc-prog-label" style="color:#657770;font-size:11px"></small>
      ${checks}
      <h4>Equipment</h4>${equipment}
      <h4>Open alerts</h4>${alertRows}
      <div style="margin-top:24px">
        <button class="mc-btn primary" id="mc-ask" type="button">Ask policy about this stage</button>
        <div class="mc-policy-box" id="mc-policy-box"></div>
      </div>`;

    const updateProgress = () => {
      const n = $$('#mc-drawer-body .mc-check input:checked').length;
      $('#mc-prog').style.width = total ? `${(n / total) * 100}%` : '0';
      $('#mc-prog-label').textContent = `${n} of ${total} checks complete`;
    };
    updateProgress();

    $$('#mc-drawer-body .mc-check input').forEach((box) => {
      box.addEventListener('change', () => {
        const ticked = $$('#mc-drawer-body .mc-check input')
          .filter((b) => b.checked).map((b) => Number(b.dataset.i));
        store.set(key, ticked);
        updateProgress();
        if (ticked.length === total) toast(`${safety.stage} checklist complete for ${d.site.name}`);
      });
    });

    $('#mc-ask').addEventListener('click', async () => {
      const box = $('#mc-policy-box');
      const stage = { id: safety.stage_id, name: safety.stage };
      if (typeof window.MineCore.askPolicy === 'function') {
        box.textContent = 'Asking the Policy Explainer…';
        try { await window.MineCore.askPolicy(stage, box); }
        catch { box.textContent = 'The Policy Explainer did not respond. Try again.'; }
        return;
      }
      try {
        const p = await api(`/api/mining/stages/${stage.id}/policy-context`);
        box.textContent = `Question for the Policy Explainer: "${p.policy_query}" It is not connected to this page yet.`;
      } catch {
        box.textContent = 'Could not load the policy context.';
      }
    });
  }
  window.MineCore.showSite = showSite;

  // Make every site card open the drawer (the "View site data" link still works as a fallback).
  $$('.site-card').forEach((card) => {
    const link = $('.site-link', card);
    if (!link) return;
    const id = link.getAttribute('href').split('/').pop();
    card.classList.add('mc-clickable');
    card.addEventListener('click', (e) => { e.preventDefault(); showSite(id); });
  });

  // ---------- lifecycle stages: click to expand ----------
  $$('.lifecycle-item').forEach((item) => {
    const id = parseInt($('.lifecycle-number', item).textContent, 10);
    item.classList.add('mc-clickable');
    item.setAttribute('role', 'button');
    item.setAttribute('aria-expanded', 'false');
    item.tabIndex = 0;

    const toggle = async () => {
      const open = item.classList.toggle('mc-open');
      item.setAttribute('aria-expanded', String(open));
      let panel = item.nextElementSibling;
      if (panel && panel.classList.contains('mc-stage-detail')) { panel.hidden = !open; return; }
      if (!open) return;
      panel = document.createElement('div');
      panel.className = 'mc-stage-detail';
      panel.textContent = 'Loading…';
      item.after(panel);
      try {
        const s = await api(`/api/mining/stages/${id}`);
        const eq = (s.equipment || []).map((e) => `${esc(e.name)} (${esc(e.status)})`).join(', ');
        panel.innerHTML = `<p>${esc(s.description)}</p>
          <ul>${s.safety_requirements.map((r) => `<li>${esc(r)}</li>`).join('')}</ul>
          ${eq ? `<p style="margin-top:10px">Equipment: ${eq}</p>` : ''}`;
      } catch {
        panel.textContent = 'Could not load stage details.';
      }
    };
    item.addEventListener('click', toggle);
    item.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); }
    });
  });

  // ---------- site search + filter ----------
  const grid = $('.site-grid');
  if (grid) {
    const toolbar = document.createElement('div');
    toolbar.className = 'mc-toolbar';
    toolbar.innerHTML = `
      <input id="mc-search" type="search" placeholder="Search sites or stages" aria-label="Search sites">
      <div class="mc-chips" role="group" aria-label="Filter by safety status">
        <button type="button" data-f="all" class="on">All</button>
        <button type="button" data-f="good">Good</button>
        <button type="button" data-f="warning">Warning</button>
      </div>`;
    const empty = document.createElement('p');
    empty.className = 'mc-empty';
    empty.hidden = true;
    empty.textContent = 'No sites match. Clear the search or pick "All".';
    grid.before(toolbar);
    grid.after(empty);

    let filter = 'all';
    const apply = () => {
      const q = $('#mc-search').value.trim().toLowerCase();
      let shown = 0;
      $$('.site-card', grid).forEach((card) => {
        const safety = $('.status-badge', card).textContent.trim().toLowerCase();
        const searchable = ['.site-name', '.site-location', '.site-stage']
          .map((sel) => ($(sel, card) || {}).textContent || '').join(' ').toLowerCase();
        const ok = (filter === 'all' || safety === filter) && searchable.includes(q);
        card.hidden = !ok;
        if (ok) shown += 1;
      });
      empty.hidden = shown > 0;
    };
    $('#mc-search').addEventListener('input', apply);
    $$('.mc-chips button', toolbar).forEach((b) => b.addEventListener('click', () => {
      filter = b.dataset.f;
      $$('.mc-chips button', toolbar).forEach((x) => x.classList.toggle('on', x === b));
      apply();
    }));
  }

  // ---------- safety alerts: resolve + report ----------
  const safetyPanel = $('#safety');
  const resolvedKey = 'mc-resolved-alerts';
  let resolved = store.get(resolvedKey, []);
  const alertKey = (card) => $('.alert-message', card).textContent.trim();

  function updateOpenAlertsStat() {
    const open = $$('.alert-card').filter((c) => !c.classList.contains('mc-resolved')).length;
    const stat = $$('.stat').find((s) => /open alerts/i.test($('.stat-label', s).textContent));
    if (stat) $('.stat-value', stat).textContent = open;
  }

  function setResolved(card, isResolved) {
    const meta = $('.alert-meta', card);
    if (!meta.dataset.orig) meta.dataset.orig = meta.textContent.replace(/\s+/g, ' ').trim();
    card.classList.toggle('mc-resolved', isResolved);
    meta.textContent = isResolved ? meta.dataset.orig.replace(/Open$/, 'Resolved') : meta.dataset.orig;
    $('.mc-btn', card).textContent = isResolved ? 'Reopen' : 'Resolve';
  }

  function wireAlert(card) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'mc-btn';
    btn.textContent = 'Resolve';
    card.appendChild(btn);
    btn.addEventListener('click', () => {
      const nowResolved = !card.classList.contains('mc-resolved');
      setResolved(card, nowResolved);
      const key = alertKey(card);
      resolved = nowResolved ? [...new Set([...resolved, key])] : resolved.filter((k) => k !== key);
      store.set(resolvedKey, resolved);
      updateOpenAlertsStat();
      toast(nowResolved ? 'Alert resolved' : 'Alert reopened');
    });
    if (resolved.includes(alertKey(card))) setResolved(card, true);
  }

  function buildAlertCard({ severity, message, site }) {
    const card = document.createElement('div');
    card.className = 'alert-card';
    card.innerHTML = `
      <div class="alert-symbol ${esc(severity.toLowerCase())}">!</div>
      <div class="alert-content">
        <div class="alert-message">${esc(message)}</div>
        <div class="alert-meta">${esc(severity)} · ${esc(site)} · Open</div>
      </div>`;
    wireAlert(card);
    return card;
  }

  if (safetyPanel) {
    $$('.alert-card', safetyPanel).forEach(wireAlert);

    const siteNames = $$('.site-card .site-name').map((n) => n.textContent.trim());
    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'mc-btn mc-report-toggle';
    toggle.textContent = '+ Report an incident';
    const form = document.createElement('div');
    form.className = 'mc-report-form';
    form.hidden = true;
    form.innerHTML = `
      <select id="mc-r-site" aria-label="Site">${siteNames.map((n) => `<option>${esc(n)}</option>`).join('')}</select>
      <select id="mc-r-sev" aria-label="Severity"><option>Low</option><option>Medium</option><option>High</option></select>
      <input id="mc-r-msg" type="text" maxlength="120" placeholder="What happened?" aria-label="Incident description">
      <button type="button" class="mc-btn primary" id="mc-r-add">Add alert</button>`;
    const anchor = $('.alert-card', safetyPanel) || $('.monitor-box', safetyPanel);
    anchor.before(toggle, form);

    // Re-create incidents reported earlier in this browser.
    const custom = store.get('mc-custom-alerts', []);
    custom.slice().reverse().forEach((a) => form.after(buildAlertCard(a)));

    toggle.addEventListener('click', () => { form.hidden = !form.hidden; if (!form.hidden) $('#mc-r-msg').focus(); });
    $('#mc-r-add').addEventListener('click', () => {
      const message = $('#mc-r-msg').value.trim();
      if (!message) { toast('Describe the incident first'); return; }
      const alertData = { severity: $('#mc-r-sev').value, message, site: $('#mc-r-site').value };
      form.after(buildAlertCard(alertData));
      store.set('mc-custom-alerts', [alertData, ...store.get('mc-custom-alerts', [])]);
      $('#mc-r-msg').value = '';
      form.hidden = true;
      updateOpenAlertsStat();
      toast(`Incident reported for ${alertData.site}`);
    });
    updateOpenAlertsStat();
  }

  // ---------- simulated live production feed ----------
  const SIMULATE_LIVE = true;   // set to false to switch the feed off
  const sitesHeader = $('#sites .section-header');
  if (SIMULATE_LIVE && sitesHeader) {
    const note = document.createElement('div');
    note.className = 'mc-live';
    note.innerHTML = '<i></i><span id="mc-live-text">Simulated live feed</span>';
    sitesHeader.after(note);
    const totalStat = $$('.stat').find((s) => /production/i.test($('.stat-label', s).textContent));

    setInterval(() => {
      let total = 0;
      $$('.site-card').forEach((card) => {
        const strong = $('.production-row strong', card);
        const status = $('.production-status', card);
        if (!strong || !status) return;
        let n = parseInt(strong.textContent.replace(/[^\d]/g, ''), 10) || 0;
        if (/^active$/i.test(status.textContent.trim())) {
          n += 1 + Math.floor(Math.random() * 6);
          strong.textContent = `${fmt(n)} tons`;
          strong.classList.remove('mc-tick');
          void strong.offsetWidth;            // restart the flash animation
          strong.classList.add('mc-tick');
        }
        total += n;
      });
      if (totalStat) {
        const value = $('.stat-value', totalStat);
        if (value.firstChild && value.firstChild.nodeType === 3) value.firstChild.nodeValue = `${fmt(total)} `;
      }
      $('#mc-live-text').textContent = `Simulated live feed · updated ${new Date().toLocaleTimeString()}`;
    }, 4000);
  }
})();