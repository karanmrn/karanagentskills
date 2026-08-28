// slides-viz server — a dependency-free local visualizer for HTML slide decks.
//
// Responsibilities:
//   - serve the deck (with sdk.js injected) inside a same-origin iframe
//   - serve the "chrome" side-panel UI (prompt composer + code editor + slide list)
//   - queue feedback the user sends from the panel
//   - answer the agent's long-poll (`slides-viz poll`) with queued feedback
//   - live-reload the browser (SSE) when the deck file changes on disk
//   - let the panel read/write the raw deck file (in-browser code editor)
//
// One server process serves exactly one deck file. State lives in memory;
// the CLI records {port,pid} per deck path in ~/.slides-viz/state.json.

const http = require('node:http');
const https = require('node:https');
const fs = require('node:fs');
const fsp = require('node:fs/promises');
const path = require('node:path');
const os = require('node:os');
const { EventEmitter } = require('node:events');

const DECK_PATH = process.env.SLIDES_VIZ_DECK;
const PORT = Number(process.env.SLIDES_VIZ_PORT || 0);

// Public deploy host (nextgen-slides-web). Overridable for staging/local hosts.
const NEXTGEN_ORIGIN = (process.env.NEXTGEN_ORIGIN || 'https://nextgenslides.dev').replace(/\/+$/, '');
// Update keys handed out by the deploy host are secrets — we keep them OUT of the
// browser entirely, in a 0600 file next to the CLI's own state (keyed by deck path).
const TOKEN_DIR = path.join(os.homedir(), '.slides-viz');
const TOKEN_FILE = path.join(TOKEN_DIR, 'tokens.json');
if (!DECK_PATH) {
  console.error('SLIDES_VIZ_DECK env var is required');
  process.exit(1);
}

const HERE = __dirname;
const VERSION = Date.now();              // identifies this server instance; a new
                                         // instance makes stale tabs full-reload
const bus = new EventEmitter();          // "reload" and "feedback" events
bus.setMaxListeners(0);

const feedbackQueue = [];                // items waiting for the agent to poll
const sentLog = [];                      // everything ever sent (for panel history)

// Agent-status inference (drives the panel's live "Listening / Applying" badge):
//   - a poll is WAITING           → agent is listening (green)
//   - a poll just returned tasks  → agent is applying them (amber) until it
//                                   re-arms the next poll (or 30s safety timeout)
let pollers = 0;
let processing = false;
let agentNote = '';
let procTimer = null;
const agentState = () => ({ listening: pollers > 0, working: processing, note: agentNote });
function setProcessing(v) {
  processing = v;
  clearTimeout(procTimer);
  if (v) procTimer = setTimeout(() => { processing = false; bus.emit('agent'); }, 30000);
  bus.emit('agent');
}

// Per-item lifecycle (drives the panel's queued → working → done badges):
//   queued   → sitting in the queue, the agent hasn't picked it up yet
//   working  → the agent drained it in a poll and is applying it
//   done     → the agent re-armed its poll, so that batch is applied
function markItems(items, status) {
  for (const it of items) if (it && it.ts != null) it.status = status;
}
function finishWorking() {
  // A fresh poll means the previous batch has been applied — mark it done.
  let changed = false;
  for (const e of sentLog) if (e.status === 'working') { e.status = 'done'; changed = true; }
  if (changed) bus.emit('agent');
}

// ---------------------------------------------------------------- helpers ---

function send(res, status, body, headers = {}) {
  res.writeHead(status, { 'Cache-Control': 'no-store', ...headers });
  res.end(body);
}
function json(res, status, obj) {
  send(res, status, JSON.stringify(obj), { 'Content-Type': 'application/json' });
}
function readBody(req) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', (c) => {
      data += c;
      if (data.length > 25 * 1024 * 1024) reject(new Error('body too large'));
    });
    req.on('end', () => resolve(data));
    req.on('error', reject);
  });
}

// Inject sdk.js right before </body> so the deck can talk to the panel.
function injectSdk(html) {
  const tag = '<script src="/__viz/sdk.js"></script>';
  const idx = html.toLowerCase().lastIndexOf('</body>');
  if (idx === -1) return html + '\n' + tag;
  return html.slice(0, idx) + tag + '\n' + html.slice(idx);
}

// ---------------------------------------------------- publish (deploy host) ---
// The whole point of proxying the upload through THIS local server (instead of
// letting the browser call the deploy host directly) is twofold: the host sends
// no CORS headers, and — more importantly — the returned updateKey is a secret
// the browser should never see or store. We hold it here, on disk, 0600.

async function readTokens() {
  try { return JSON.parse(await fsp.readFile(TOKEN_FILE, 'utf8')); } catch { return {}; }
}
async function writeTokens(all) {
  await fsp.mkdir(TOKEN_DIR, { recursive: true });
  await fsp.writeFile(TOKEN_FILE, JSON.stringify(all, null, 2), { mode: 0o600 });
  try { await fsp.chmod(TOKEN_FILE, 0o600); } catch {}   // enforce even if the file pre-existed
}
const getToken = async () => (await readTokens())[DECK_PATH] || null;
async function setToken(rec) { const all = await readTokens(); all[DECK_PATH] = rec; await writeTokens(all); }
async function clearToken() { const all = await readTokens(); delete all[DECK_PATH]; await writeTokens(all); }

// A deck that exposes window.videoDirector is a "video"; otherwise a "deck".
// Title comes straight from the document's <title> so the listing reads nicely.
function deckMeta(html) {
  const type = /videoDirector/.test(html) ? 'video' : 'deck';
  const m = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  const title = (m ? m[1] : '').replace(/\s+/g, ' ').trim().slice(0, 200);
  return { type, title };
}

// Minimal one-shot HTTPS/HTTP request to the deploy host (raw text/html body).
function remoteRequest(method, url, { body = null, bearer = null } = {}) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const lib = u.protocol === 'https:' ? https : http;
    const data = body != null ? Buffer.from(body, 'utf8') : null;
    const req = lib.request(
      {
        method,
        hostname: u.hostname,
        port: u.port || (u.protocol === 'https:' ? 443 : 80),
        path: u.pathname + u.search,
        headers: {
          'Content-Type': 'text/html; charset=utf-8',
          ...(data ? { 'Content-Length': data.length } : {}),
          ...(bearer ? { Authorization: 'Bearer ' + bearer } : {}),
        },
      },
      (res) => { let d = ''; res.on('data', (c) => (d += c)); res.on('end', () => resolve({ status: res.statusCode, body: d })); }
    );
    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

// ---------------------------------------------------------- file watching ---

let reloadTimer = null;
function scheduleReload() {
  clearTimeout(reloadTimer);
  reloadTimer = setTimeout(() => bus.emit('reload'), 120); // debounce editor saves + editor churn
}
try {
  fs.watch(DECK_PATH, { persistent: true }, scheduleReload);
} catch (e) {
  console.error('warn: could not watch deck file:', e.message);
}

// ------------------------------------------------------------- the server ---

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const p = url.pathname;

  try {
    // --- health / lifecycle -------------------------------------------------
    if (p === '/__viz/health') return json(res, 200, { ok: true, deck: DECK_PATH });
    if (p === '/__viz/end' && req.method === 'POST') {
      json(res, 200, { ok: true });
      finishWorking();                  // settle any in-flight badges before we close
      bus.emit('end');
      setTimeout(() => process.exit(0), 50);
      return;
    }

    // --- static assets of the visualizer itself -----------------------------
    // The editor shell depends on the deck TYPE: a deck that exposes
    // window.videoDirector is a "video" → the video editor; otherwise the
    // slides editor. Both shells share ui/editor-core.js + ui/editor.css.
    if (p === '/' || p === '/index.html') {
      const deckSrc = await fsp.readFile(DECK_PATH, 'utf8');
      const shell = /videoDirector/.test(deckSrc) ? 'chrome-video.html' : 'chrome-slides.html';
      const html = await fsp.readFile(path.join(HERE, 'ui', shell), 'utf8');
      return send(res, 200, html, { 'Content-Type': 'text/html; charset=utf-8' });
    }
    if (p === '/__viz/sdk.js') {
      const js = await fsp.readFile(path.join(HERE, 'sdk.js'), 'utf8');
      return send(res, 200, js, { 'Content-Type': 'text/javascript; charset=utf-8' });
    }
    // shared editor UI assets (css / core js / either shell if requested directly)
    if (p.startsWith('/__viz/ui/')) {
      const name = p.slice('/__viz/ui/'.length);
      if (!/^[a-z0-9._-]+$/i.test(name)) return json(res, 400, { error: 'bad asset name' });
      const TYPES = { '.css': 'text/css', '.js': 'text/javascript', '.html': 'text/html' };
      const ext = path.extname(name).toLowerCase();
      const body = await fsp.readFile(path.join(HERE, 'ui', name), 'utf8');
      return send(res, 200, body, { 'Content-Type': (TYPES[ext] || 'text/plain') + '; charset=utf-8' });
    }

    // --- the deck, with sdk injected, in the iframe -------------------------
    if (p === '/__viz/deck') {
      const html = await fsp.readFile(DECK_PATH, 'utf8');
      return send(res, 200, injectSdk(html), { 'Content-Type': 'text/html; charset=utf-8' });
    }
    // --- "Preview": the clean deck (it scales its own fixed 1920×1080 stage to
    //     fit any window — whole slide always visible, no editor chrome). -------
    if (p === '/__viz/preview' || p === '/__viz/preview-raw') {
      const html = await fsp.readFile(DECK_PATH, 'utf8');
      return send(res, 200, html, { 'Content-Type': 'text/html; charset=utf-8' });
    }

    // --- agent status (the panel's live "Listening / Applying" indicator) ---
    if (p === '/__viz/agent' && req.method === 'POST') {
      const s = JSON.parse(await readBody(req));   // optional: annotate what we're doing
      agentNote = String(s.note || '').slice(0, 200);
      bus.emit('agent');
      return json(res, 200, { ok: true });
    }

    // --- raw deck source for the in-browser code editor --------------------
    if (p === '/__viz/raw') {
      const src = await fsp.readFile(DECK_PATH, 'utf8');
      return json(res, 200, { source: src, path: DECK_PATH });
    }
    if (p === '/__viz/save' && req.method === 'POST') {
      const { source } = JSON.parse(await readBody(req));
      if (typeof source !== 'string') return json(res, 400, { error: 'source required' });
      await fsp.writeFile(DECK_PATH, source, 'utf8'); // fs.watch will trigger reload
      return json(res, 200, { ok: true });
    }

    // --- publish to the public deploy host ---------------------------------
    // Has this deck been published before? (drives the dialog's create-vs-update
    // wording and the "live at …" link). We never expose the updateKey.
    if (p === '/__viz/publish-status') {
      const rec = await getToken();
      return json(res, 200, {
        origin: NEXTGEN_ORIGIN,
        published: !!rec,
        id: rec ? rec.id : null,
        url: rec ? rec.url : null,
        hasPassword: rec ? !!rec.hasPassword : false,
      });
    }
    // Upload the current deck file. First publish → POST (returns id/updateKey,
    // which we stash); thereafter → PUT with the stored key to overwrite in place.
    if (p === '/__viz/publish' && req.method === 'POST') {
      const raw = await readBody(req);
      const opts = raw ? JSON.parse(raw) : {};
      const password = typeof opts.password === 'string' ? opts.password.trim() : '';
      const html = await fsp.readFile(DECK_PATH, 'utf8');
      const { type, title } = deckMeta(html);
      const rec = await getToken();

      if (rec && rec.updateKey) {
        // Update the existing deployment. A password is only sent when the user
        // typed one (the host keeps the old one on an empty value — can't clear).
        const q = password ? '?password=' + encodeURIComponent(password) : '';
        const r = await remoteRequest('PUT', `${NEXTGEN_ORIGIN}/api/deploy/${rec.id}${q}`, { body: html, bearer: rec.updateKey });
        if (r.status === 401) { await clearToken(); return json(res, 409, { error: 'The stored update key was rejected. Publish again to create a fresh deployment.' }); }
        if (r.status !== 204 && r.status !== 200) return json(res, 502, { error: 'Update failed (' + r.status + ')', detail: r.body.slice(0, 200) });
        if (password) { rec.hasPassword = true; await setToken(rec); }
        return json(res, 200, { updated: true, id: rec.id, url: rec.url, hasPassword: !!rec.hasPassword });
      }

      // First publish.
      const qs = new URLSearchParams({ type });
      if (title) qs.set('title', title);
      if (password) qs.set('password', password);
      const r = await remoteRequest('POST', `${NEXTGEN_ORIGIN}/api/deploy?${qs}`, { body: html });
      if (r.status !== 201) return json(res, 502, { error: 'Publish failed (' + r.status + ')', detail: r.body.slice(0, 200) });
      let out; try { out = JSON.parse(r.body); } catch { return json(res, 502, { error: 'Bad response from deploy host' }); }
      await setToken({ id: out.id, url: out.url, updateKey: out.updateKey, hasPassword: !!password });
      return json(res, 200, { created: true, id: out.id, url: out.url, hasPassword: !!password });
    }

    // --- feedback from the side panel --------------------------------------
    if (p === '/__viz/feedback' && req.method === 'POST') {
      const item = JSON.parse(await readBody(req));
      const entry = {
        message: String(item.message || '').slice(0, 8000),
        slide: item.slide ?? null,          // 1-based slide number
        selector: item.selector ?? null,    // CSS selector of clicked element
        snippet: item.snippet ?? null,      // small outerHTML excerpt
        time: item.time ?? null,            // video timecode (e.g. "0:06"), null for slides
        ts: sentLog.length + 1,             // monotonic id (no Date in sandbox-safe path)
        status: 'queued',                   // queued → working → done
      };
      if (!entry.message) return json(res, 400, { error: 'message required' });
      feedbackQueue.push(entry);
      sentLog.push(entry);
      bus.emit('feedback');
      return json(res, 200, { ok: true, queued: feedbackQueue.length });
    }
    // Panel history (what has been sent so far this session).
    if (p === '/__viz/history') return json(res, 200, { sent: sentLog });

    // --- agent long-poll: drain the queue, or wait for it to fill ----------
    if (p === '/__viz/poll') {
      finishWorking();                  // a new poll ⇒ the previous batch is applied → done
      if (feedbackQueue.length) {
        const items = feedbackQueue.splice(0);
        markItems(items, 'working');    // picked up → panel shows the spinner on these
        setProcessing(true);            // returned tasks → panel shows "Applying"
        return json(res, 200, { items, pending: 0 });
      }
      let done = false;
      pollers++; setProcessing(false);  // waiting → panel shows "Listening"
      const finish = (items) => {
        if (done) return;
        done = true;
        pollers = Math.max(0, pollers - 1);
        markItems(items, 'working');    // picked up → spinner on these items
        setProcessing(true);            // got tasks → "Applying" until we re-arm
        clearInterval(hb);
        bus.off('feedback', onFb);
        bus.off('end', onEnd);
        res.end(JSON.stringify({ items, pending: 0 }));
      };
      const onFb = () => finish(feedbackQueue.splice(0));
      const onEnd = () => finish([{ message: '__session_ended__', slide: null }]);
      res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
      const hb = setInterval(() => { if (!done) res.write(' '); }, 15000); // heartbeat
      bus.once('feedback', onFb);
      bus.once('end', onEnd);
      req.on('close', () => {
        if (!done) { done = true; pollers = Math.max(0, pollers - 1); bus.emit('agent'); }
        clearInterval(hb); bus.off('feedback', onFb); bus.off('end', onEnd);
      });
      return;
    }

    // --- SSE: live-reload channel for the browser --------------------------
    if (p === '/__viz/events') {
      res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-store',
        Connection: 'keep-alive',
      });
      res.write('retry: 1000\n\n');
      res.write(`event: hello\ndata: ${JSON.stringify({ v: VERSION })}\n\n`);
      res.write(`event: agent\ndata: ${JSON.stringify(agentState())}\n\n`);
      const onReload = () => res.write('event: reload\ndata: {}\n\n');
      const onEnd = () => res.write('event: end\ndata: {}\n\n');
      const onAgent = () => res.write(`event: agent\ndata: ${JSON.stringify(agentState())}\n\n`);
      const hb = setInterval(() => res.write(': ping\n\n'), 20000);
      bus.on('reload', onReload);
      bus.on('end', onEnd);
      bus.on('agent', onAgent);
      req.on('close', () => { clearInterval(hb); bus.off('reload', onReload); bus.off('end', onEnd); bus.off('agent', onAgent); });
      return;
    }

    return json(res, 404, { error: 'not found', path: p });
  } catch (err) {
    return json(res, 500, { error: err.message });
  }
});

server.listen(PORT, '127.0.0.1', () => {
  const addr = server.address();
  // The CLI reads this line to learn the actual port when PORT was 0.
  console.log(`SLIDES_VIZ_LISTENING ${addr.port}`);
});
