/* ============================================================================
   editor-core.js — SHARED logic for both editors (slides + video).
   Everything deck-type-agnostic lives here: same-origin deck control, inline
   text editing, click-to-comment, the feedback queue, sent-history + per-item
   status badges, the agent status bar, live-reload SSE, save, and the help /
   Done-&-Close dialogs.

   The slides and video shells each provide a small ADAPTER for what differs:
   the top-bar controls (slide nav vs. transport) and the "where does this
   comment attach" context (a slide number vs. a video timecode).

   Adapter shape:
     {
       initControls(core)          // wire mode-specific top-bar buttons ONCE
       onBind(core)                // per deck (re)load (core.getDoc() is ready)
       onDeckKeyup(core)           // optional: in-deck keyup (slides sync nav)
       commentContext(core, {pause}) -> { slide?, time? }   // comment anchor
     }
   `core` exposes: { $, deck, stage, getDoc, closePopup, renderHistory, tfmt }.
   ========================================================================== */
window.initEditor = function initEditor(adapter) {
  const $ = (s) => document.querySelector(s);
  const deck = $('#deck');
  const stage = $('#stage');
  let curTarget = null;
  const pending = [];
  // The deck scales ITSELF (fixed 1920×1080 stage inside the deck file), so the
  // iframe just fills the stage area 1:1 — no outer scaling / coordinate mapping.
  addEventListener('resize', closePopup);

  // ---- direct same-origin control of the deck document --------------------
  let doc = null, selectedEl = null, hoverEl = null;
  let editingEl = null, editingOrig = null;
  let clickTimer = null;

  const tfmt = (ms) => { const s = Math.max(0, Math.round((ms || 0) / 1000)); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'); };

  // Small surface handed to the mode adapter. Defined UP HERE (not at the end)
  // because the deck iframe may already be loaded, so bindDeck() — which calls
  // adapter.onBind(core) — can fire before initEditor finishes. closePopup /
  // renderHistory are hoisted function declarations, so this reference is safe.
  const core = { $, deck, stage, getDoc: () => doc, closePopup, renderHistory, tfmt };

  function selectorFor(el) {
    if (!el || el === doc.body) return 'body';
    if (el.id) return '#' + CSS.escape(el.id);
    const parts = []; let node = el;
    while (node && node.nodeType === 1 && node !== doc.body && parts.length < 5) {
      let seg = node.tagName.toLowerCase();
      const cls = Array.from(node.classList)
        .filter((c) => !c.startsWith('viz-') && c !== 'active' && c !== 'visible').slice(0, 2);
      if (cls.length) seg += '.' + cls.map((c) => CSS.escape(c)).join('.');
      const parent = node.parentElement;
      if (parent) {
        const sibs = Array.from(parent.children).filter((c) => c.tagName === node.tagName);
        if (sibs.length > 1) seg += ':nth-of-type(' + (sibs.indexOf(node) + 1) + ')';
      }
      parts.unshift(seg);
      if (node.id) { parts[0] = '#' + CSS.escape(node.id); break; }
      node = parent;
    }
    return parts.join(' > ');
  }

  function setHover(el) {
    if (hoverEl && hoverEl !== selectedEl) hoverEl.classList.remove('viz-hover');
    hoverEl = el;
    if (hoverEl && hoverEl !== selectedEl && hoverEl !== editingEl) hoverEl.classList.add('viz-hover');
  }
  function setSelected(el) {
    if (selectedEl) selectedEl.classList.remove('viz-selected');
    selectedEl = el;
    if (selectedEl) { selectedEl.classList.add('viz-selected'); selectedEl.classList.remove('viz-hover'); }
  }

  // ---- inline text editing -------------------------------------------------
  function startEdit(el) {
    if (editingEl || !el || el === doc.body) return;
    clearTimeout(clickTimer);
    closePopup();
    setSelected(null); setHover(null);
    editingEl = el; editingOrig = el.innerHTML;
    el.setAttribute('contenteditable', 'true');
    el.classList.add('viz-editing');
    el.focus();
    const r = doc.createRange(); r.selectNodeContents(el);
    const sel = deck.contentWindow.getSelection(); sel.removeAllRanges(); sel.addRange(r);
  }
  function commitEdit() {
    if (!editingEl) return;
    const el = editingEl; editingEl = null;
    el.removeAttribute('contenteditable'); el.classList.remove('viz-editing');
    persist();
  }
  function cancelEdit() {
    if (!editingEl) return;
    const el = editingEl; editingEl = null;
    el.innerHTML = editingOrig;
    el.removeAttribute('contenteditable'); el.classList.remove('viz-editing');
    el.blur();
  }
  function cleanSource() {
    const html = doc.documentElement.cloneNode(true);
    html.querySelectorAll('script[src="/__viz/sdk.js"], #viz-style').forEach((n) => n.remove());
    html.querySelectorAll('[contenteditable]').forEach((n) => n.removeAttribute('contenteditable'));
    html.querySelectorAll('.viz-hover, .viz-selected, .viz-editing').forEach((n) => {
      n.classList.remove('viz-hover', 'viz-selected', 'viz-editing');
      if (!n.getAttribute('class')) n.removeAttribute('class');
    });
    return '<!DOCTYPE html>\n' + html.outerHTML;
  }
  async function persist() {
    await fetch('/__viz/save', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ source: cleanSource() }) });
    const t = $('#savetoast'); t.classList.add('show'); setTimeout(() => t.classList.remove('show'), 1200);
  }

  function bindDeck() {
    try { doc = deck.contentDocument || deck.contentWindow.document; } catch (e) { doc = null; }
    if (adapter.onBind) adapter.onBind(core);      // per (re)load: mode wires nav/transport
    if (!doc || doc.__vizBound) return;
    doc.__vizBound = true;

    let st = doc.getElementById('viz-style');
    if (!st) { st = doc.createElement('style'); st.id = 'viz-style'; doc.head && doc.head.appendChild(st); }
    st.textContent =
      '*{cursor:crosshair!important}' +
      '.viz-hover{outline:2px dashed #4f8cff!important;outline-offset:2px}' +
      '.viz-selected{outline:2px solid #4f8cff!important;outline-offset:2px;box-shadow:0 0 0 4px rgba(79,140,255,.25)!important}' +
      '.viz-editing,.viz-editing *{cursor:text!important}' +
      '.viz-editing{outline:2px solid #35c07f!important;outline-offset:3px;box-shadow:0 0 0 4px rgba(53,192,127,.22)!important}';

    doc.addEventListener('mousemove', (e) => {
      if (editingEl) return;
      const el = doc.elementFromPoint(e.clientX, e.clientY);
      if (el && el !== hoverEl) setHover(el);
    }, true);

    doc.addEventListener('click', (e) => {
      if (editingEl) return;
      const el = e.target;
      if (!el || el === doc.documentElement || el === doc.body) return;
      e.preventDefault(); e.stopPropagation();
      // rect is already in stage-area coords (iframe fills the stage 1:1)
      const r = el.getBoundingClientRect();
      const ctx = (adapter.commentContext && adapter.commentContext(core, { pause: true })) || {};
      const payload = {
        selector: selectorFor(el),
        snippet: (el.outerHTML || '').replace(/\s+/g, ' ').slice(0, 240),
        slide: ctx.slide ?? null,
        time: ctx.time || null,
        rect: { x: r.left, y: r.top, w: r.width, h: r.height },
      };
      if (ctx.time) payload.snippet = '@' + ctx.time + ' · ' + payload.snippet;  // stamp WHEN for the agent
      clearTimeout(clickTimer);
      clickTimer = setTimeout(() => { setSelected(el); openPopup(payload); }, 230);
    }, true);

    doc.addEventListener('dblclick', (e) => {
      const el = e.target;
      if (!el || el === doc.documentElement) return;
      e.preventDefault(); e.stopPropagation();
      startEdit(el);
    }, true);

    doc.addEventListener('keydown', (e) => {
      if (!editingEl) return;
      e.stopPropagation();
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); editingEl.blur(); }
      else if (e.key === 'Escape') { e.preventDefault(); cancelEdit(); }
    }, false);
    doc.addEventListener('blur', (e) => { if (editingEl && e.target === editingEl) commitEdit(); }, true);

    doc.addEventListener('keyup', () => { if (adapter.onDeckKeyup) adapter.onDeckKeyup(core); }, true);
  }
  deck.addEventListener('load', bindDeck);
  if (deck.contentDocument && deck.contentDocument.readyState === 'complete') bindDeck();

  $('#preview').onclick = () => window.open('/__viz/preview', '_blank');

  // ---- manual deck refresh -------------------------------------------------
  // Re-fetches the deck HTML and rebinds — recovers from a stuck live-reload or
  // a structural change (e.g. a newly added slide) that left the view desynced.
  function reloadDeck() {
    closePopup(); selectedEl = null; hoverEl = null;
    if (deck.contentWindow) { try { deck.contentWindow.location.reload(); return; } catch (e) {} }
    deck.src = deck.src;
  }
  const refreshBtn = $('#refresh');
  if (refreshBtn) refreshBtn.onclick = reloadDeck;   // a menu item; the menu closes itself on click

  // ---- download the deck as a standalone .html file ------------------------
  const downloadBtn = $('#download');
  if (downloadBtn) downloadBtn.onclick = async () => {
    try {
      const { source, path } = await (await fetch('/__viz/raw')).json();
      const name = (path || 'deck.html').split(/[\\/]/).pop() || 'deck.html';
      const a = document.createElement('a');
      a.href = URL.createObjectURL(new Blob([source], { type: 'text/html' }));
      a.download = name;
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    } catch (e) {}
  };

  // ---- help dialog ---------------------------------------------------------
  const modal = $('#modal');
  $('#help').onclick = () => modal.classList.add('show');
  $('#modal-close').onclick = () => modal.classList.remove('show');
  modal.addEventListener('click', (e) => { if (e.target === modal) modal.classList.remove('show'); });
  addEventListener('keydown', (e) => { if (e.key === 'Escape') modal.classList.remove('show'); });

  // ---- Continue (end the session so the agent stops polling) --------------
  const confirmDlg = $('#confirm');
  $('#done').onclick = () => confirmDlg.classList.add('show');
  $('#confirm-cancel').onclick = () => confirmDlg.classList.remove('show');
  confirmDlg.addEventListener('click', (e) => { if (e.target === confirmDlg) confirmDlg.classList.remove('show'); });
  addEventListener('keydown', (e) => { if (e.key === 'Escape') confirmDlg.classList.remove('show'); });
  $('#confirm-ok').onclick = async () => {
    confirmDlg.classList.remove('show');
    try { await fetch('/__viz/end', { method: 'POST' }); } catch (e) {}
    // the server emits `end` → the SSE handler swaps the body to "Session ended."
  };

  // ---- overflow menu (Help / Preview / Publish) ----------------------------
  (function initMenu() {
    const menu = $('#menu'), btn = $('#menubtn');
    if (!menu || !btn) return;
    const close = () => { menu.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); };
    btn.onclick = (e) => {
      e.stopPropagation();
      const open = menu.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    };
    $('#menulist').addEventListener('click', close);     // choosing an item dismisses the menu
    addEventListener('click', (e) => { if (!menu.contains(e.target)) close(); });
    addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
  })();

  // ---- Publish to the public deploy host -----------------------------------
  // The local server does the actual upload (and safely keeps the returned
  // update key on disk) — the browser just collects an optional password and
  // shows the resulting public URL. Both editor shells provide the markup.
  (function initPublish() {
    const dlg = $('#publish'); const openBtn = $('#publishbtn');
    if (!dlg || !openBtn) return;
    const menuBtn = $('#menubtn');   // the ⋯ trigger — shows the published state while the menu is closed
    const pw = $('#publish-pw'), go = $('#publish-go'), err = $('#publish-err');
    const result = $('#publish-result'), urlIn = $('#publish-url');
    const openLink = $('#publish-openlink'), copyBtn = $('#publish-copy');
    let published = false;

    const setLive = (v) => { openBtn.classList.toggle('live', v); if (menuBtn) menuBtn.classList.toggle('live', v); };
    const close = () => dlg.classList.remove('show');
    const showErr = (m) => { err.textContent = m; err.classList.add('show'); };

    async function refreshStatus() {
      err.classList.remove('show'); result.classList.remove('show');
      try {
        const s = await (await fetch('/__viz/publish-status')).json();
        published = !!s.published;
        setLive(published);
        $('#publish-title').textContent = published ? 'Update your published deck' : 'Publish to the web';
        $('#publish-desc').textContent = published
          ? 'Overwrite the deck already live at the link below with the current version.'
          : 'Upload this deck to a free public URL on ' + (s.origin || 'the deploy host').replace(/^https?:\/\//, '') + '. Anyone with the link can view it.';
        go.textContent = published ? 'Update ▸' : 'Publish ▸';
        pw.placeholder = published
          ? (s.hasPassword ? 'Leave blank to keep the current password' : 'Add a password (optional)')
          : 'Leave blank for no password';
        if (published && s.url) { urlIn.value = s.url; openLink.href = s.url; result.classList.add('show'); }
      } catch (e) { /* offline status is non-fatal; user can still try to publish */ }
    }

    openBtn.onclick = () => { pw.value = ''; dlg.classList.add('show'); refreshStatus().then(() => pw.focus()); };
    $('#publish-close').onclick = close;
    $('#publish-cancel').onclick = close;
    dlg.addEventListener('click', (e) => { if (e.target === dlg) close(); });

    go.onclick = async () => {
      err.classList.remove('show');
      go.disabled = true; const label = go.textContent; go.textContent = published ? 'Updating…' : 'Publishing…';
      try {
        const r = await fetch('/__viz/publish', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ password: pw.value }),
        });
        const data = await r.json().catch(() => ({}));
        if (!r.ok) { showErr(data.error || 'Publish failed. Please try again.'); return; }
        published = true; setLive(true);
        urlIn.value = data.url; openLink.href = data.url; result.classList.add('show');
        $('#publish-title').textContent = 'Published ✓';
        $('#publish-desc').textContent = 'Your deck is live. Re-publish anytime to push the latest version to the same link.';
        go.textContent = 'Update ▸'; pw.value = '';
        return;
      } catch (e) { showErr('Could not reach the server. Is the editor still running?'); }
      finally { go.disabled = false; if (go.textContent === 'Publishing…' || go.textContent === 'Updating…') go.textContent = label; }
    };

    copyBtn.onclick = async () => {
      try { await navigator.clipboard.writeText(urlIn.value); }
      catch (e) { urlIn.select(); document.execCommand && document.execCommand('copy'); }
      const t = copyBtn.textContent; copyBtn.textContent = 'Copied ✓';
      setTimeout(() => { copyBtn.textContent = t; }, 1200);
    };

    addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
  })();

  // ---- live agent status ---------------------------------------------------
  function updateAgent(s) {
    const bar = $('#agentbar');
    bar.classList.remove('listening', 'working');
    const txt = bar.querySelector('.txt');
    if (s.working) { bar.classList.add('working'); txt.textContent = s.note || 'Working…'; }
    else if (s.listening) { bar.classList.add('listening'); txt.textContent = 'Listening for changes'; }
    else { txt.textContent = 'Agent not listening'; }
    renderHistory();  // item badges advance in lockstep with the agent state
  }

  // ---- comment popup -------------------------------------------------------
  function openPopup(d) {
    curTarget = { slide: d.slide, selector: d.selector, snippet: d.snippet };
    const pop = $('#popup');
    $('#popup-sel').textContent = (d.time ? '@' + d.time : 'slide ' + (d.slide ?? '?')) + ' · ' + d.selector;
    $('#popup-text').value = '';
    pop.classList.add('show');
    const s = stage.getBoundingClientRect();
    const pw = 300, ph = 150;
    let left = d.rect ? d.rect.x : 40;
    let top = d.rect ? d.rect.y + d.rect.h + 8 : 48;
    if (left + pw > s.width) left = Math.max(8, s.width - pw - 8);
    if (top + ph > s.height) top = Math.max(8, (d.rect ? d.rect.y : 40) - ph - 8);
    pop.style.left = Math.max(8, left) + 'px';
    pop.style.top = Math.max(8, top) + 'px';
    $('#popup-text').focus();
  }
  function closePopup() { $('#popup').classList.remove('show'); curTarget = null; setSelected(null); }
  $('#popup-cancel').onclick = closePopup;
  $('#popup-add').onclick = addFromPopup;
  $('#popup-text').addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closePopup();
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') addFromPopup();
  });
  function addFromPopup() {
    const comment = $('#popup-text').value.trim();
    if (!comment || !curTarget) return closePopup();
    pending.push(Object.assign({}, curTarget, { message: comment }));
    closePopup(); renderQueue();
  }

  // ---- pending queue -------------------------------------------------------
  function renderQueue() {
    const wrap = $('#queuewrap'), list = $('#queuelist');
    $('#queuecount').textContent = pending.length + ' queued';
    wrap.classList.toggle('show', pending.length > 0);
    list.innerHTML = pending.map((p, i) =>
      '<div class="qitem"><button class="rm" data-i="' + i + '" title="Remove">✕</button>' +
      '<div class="meta">' +
        (p.slide ? '<span class="chip">slide ' + p.slide + '</span>' : '') +
        (p.time ? '<span class="chip">@' + p.time + '</span>' : '') +
        (p.selector ? '<span class="chip sel">' + escapeHtml(p.selector) + '</span>' : '') +
      '</div><div class="body">' + escapeHtml(p.message) + '</div></div>'
    ).join('');
    list.querySelectorAll('.rm').forEach((b) => b.onclick = () => { pending.splice(+b.dataset.i, 1); renderQueue(); });
  }

  async function flush(items) {
    for (const it of items) {
      await fetch('/__viz/feedback', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(it) });
    }
    renderHistory();
  }
  $('#sendqueue').onclick = async () => { if (!pending.length) return; const items = pending.splice(0); renderQueue(); await flush(items); };
  function addComposerToQueue() {
    const message = $('#msg').value.trim();
    if (!message) return;
    const ctx = (adapter.commentContext && adapter.commentContext(core, { pause: false })) || {};
    pending.push({ message, slide: ctx.slide ?? null, time: ctx.time || null, selector: null, snippet: null });
    $('#msg').value = ''; renderQueue();
  }
  $('#addmsg').onclick = addComposerToQueue;
  $('#msg').addEventListener('keydown', (e) => { if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') { e.preventDefault(); addComposerToQueue(); } });

  // ---- sent history + per-item status badges -------------------------------
  const STATUS = {
    queued:  { label: 'Queued',  title: 'Waiting for the agent to pick it up' },
    working: { label: 'Working', title: 'The agent is applying this' },
    done:    { label: 'Done',    title: 'Applied by the agent' },
  };
  function statusBadge(st) {
    const s = STATUS[st] || STATUS.queued;
    const mk = st === 'done' ? '✓' : '';
    return '<span class="st ' + (st || 'queued') + '" title="' + s.title + '">' +
      '<span class="mk">' + mk + '</span>' + s.label + '</span>';
  }
  let histSig = '';
  async function renderHistory() {
    const r = await fetch('/__viz/history'); const { sent } = await r.json();
    const h = $('#history');
    if (!sent.length) return;
    const sig = sent.map((m) => m.ts + ':' + (m.status || '')).join(',');
    if (sig === histSig) return;                     // skip DOM churn when nothing changed
    const atBottom = h.scrollHeight - h.scrollTop - h.clientHeight < 40;
    histSig = sig;
    h.innerHTML = sent.map((m) =>
      '<div class="msg ' + (m.status || 'queued') + '">' +
        '<div class="meta">' +
          (m.slide ? '<span class="chip">slide ' + m.slide + '</span>' : '') +
          (m.time ? '<span class="chip">@' + m.time + '</span>' : '') +
          '<span class="spacer"></span>' + statusBadge(m.status) +
        '</div>' +
        (m.selector ? '<div class="meta"><span class="chip sel">' + escapeHtml(m.selector) + '</span></div>' : '') +
        '<div>' + escapeHtml(m.message) + '</div>' +
      '</div>'
    ).join('');
    if (atBottom) h.scrollTop = h.scrollHeight;
  }
  const escapeHtml = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  // ---- live reload (SSE) ---------------------------------------------------
  const es = new EventSource('/__viz/events');
  let serverV = null;
  es.addEventListener('hello', (e) => {
    try { const v = JSON.parse(e.data).v; if (serverV !== null && v !== serverV) { location.reload(); return; } serverV = v; } catch (err) {}
  });
  es.addEventListener('agent', (e) => { try { updateAgent(JSON.parse(e.data)); } catch (err) {} });
  es.addEventListener('reload', () => { if (editingEl) return; reloadDeck(); });
  es.addEventListener('end', () => { document.body.innerHTML = '<div class="empty" style="margin-top:20vh">Session ended.</div>'; });

  // ---- kick things off -----------------------------------------------------
  if (adapter.initControls) adapter.initControls(core);
  renderHistory();
  setInterval(renderHistory, 4000);
  return core;
};
