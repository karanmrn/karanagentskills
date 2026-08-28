#!/usr/bin/env node
// slides-viz — CLI for the HTML-slides visualizer.
//
//   slides-viz launch <deck.html>   start (or reuse) the server, open the browser
//   slides-viz poll   <deck.html>   long-poll for feedback the user sent in the panel
//   slides-viz end    <deck.html>   close the session / stop the server
//   slides-viz status <deck.html>   print session info
//
// One server process per deck file. Session state (port, pid) is recorded in
// ~/.slides-viz/state.json keyed by the deck's absolute path.

const { spawn } = require('node:child_process');
const fs = require('node:fs');
const fsp = require('node:fs/promises');
const path = require('node:path');
const os = require('node:os');
const http = require('node:http');

const SERVER = path.join(__dirname, '..', 'server.js');
const STATE_DIR = path.join(os.homedir(), '.slides-viz');
const STATE_FILE = path.join(STATE_DIR, 'state.json');
const REF = path.join(__dirname, '..', '..', 'references');
const TEMPLATES = {
  outline: path.join(REF, 'outline-template.html'),  // white content canvas (default)
  deck: path.join(REF, 'deck-template.html'),        // styled starter deck
};

function usage() {
  console.error('usage: slides-viz <new|launch|poll|end|status> <deck.html> [outline|deck]');
  process.exit(2);
}

// Create a fresh deck file from a template (baked-in page-swap JS + live counter).
async function scaffold(deck, kind) {
  const tpl = TEMPLATES[kind] || TEMPLATES.outline;
  await fsp.writeFile(deck, await fsp.readFile(tpl, 'utf8'), 'utf8');
}
async function newDeck(deck, kind) {
  if (fs.existsSync(deck)) { console.error('file already exists: ' + deck + ' (delete it first)'); process.exit(1); }
  await scaffold(deck, kind);
  console.log(`created ${path.basename(deck)} (${kind === 'deck' ? 'styled deck' : 'outline'}). launch it with: slides-viz launch ${deck}`);
}

async function readState() {
  try { return JSON.parse(await fsp.readFile(STATE_FILE, 'utf8')); } catch { return {}; }
}
async function writeState(state) {
  await fsp.mkdir(STATE_DIR, { recursive: true });
  await fsp.writeFile(STATE_FILE, JSON.stringify(state, null, 2));
}

function get(port, p) {
  return new Promise((resolve, reject) => {
    const req = http.get({ host: '127.0.0.1', port, path: p, timeout: 0 }, (res) => {
      let d = '';
      res.on('data', (c) => (d += c));
      res.on('end', () => resolve({ status: res.statusCode, body: d }));
    });
    req.on('error', reject);
  });
}
function post(port, p, body) {
  return new Promise((resolve, reject) => {
    const data = Buffer.from(JSON.stringify(body || {}));
    const req = http.request(
      { host: '127.0.0.1', port, path: p, method: 'POST', headers: { 'Content-Type': 'application/json', 'Content-Length': data.length } },
      (res) => { let d = ''; res.on('data', (c) => (d += c)); res.on('end', () => resolve({ status: res.statusCode, body: d })); }
    );
    req.on('error', reject);
    req.end(data);
  });
}

async function healthy(port, deck) {
  try {
    const r = await get(port, '/__viz/health');
    if (r.status !== 200) return false;
    const j = JSON.parse(r.body);
    return j.ok && j.deck === deck;
  } catch { return false; }
}

async function sessionFor(deck) {
  const state = await readState();
  const s = state[deck];
  if (s && (await healthy(s.port, deck))) return s;
  return null;
}

function openBrowser(url) {
  const cmd = process.platform === 'darwin' ? 'open'
    : process.platform === 'win32' ? 'cmd' : 'xdg-open';
  const args = process.platform === 'win32' ? ['/c', 'start', '', url] : [url];
  try { spawn(cmd, args, { stdio: 'ignore', detached: true }).unref(); } catch {}
}

async function launch(deck, kind) {
  // Starting on a missing file scaffolds one from a template (outline by default).
  if (!fs.existsSync(deck)) {
    await scaffold(deck, kind);
    console.log(`scaffolded ${path.basename(deck)} (${kind === 'deck' ? 'styled deck' : 'outline'})`);
  }
  const existing = await sessionFor(deck);
  if (existing) {
    const url = `http://127.0.0.1:${existing.port}/`;
    openBrowser(url);
    console.log(`reusing session → ${url}`);
    return;
  }

  await fsp.mkdir(STATE_DIR, { recursive: true });
  const logPath = path.join(STATE_DIR, 'server-' + Buffer.from(deck).toString('hex').slice(0, 12) + '.log');
  const out = fs.openSync(logPath, 'w');
  const child = spawn(process.execPath, [SERVER], {
    detached: true,
    stdio: ['ignore', out, out],
    env: { ...process.env, SLIDES_VIZ_DECK: deck, SLIDES_VIZ_PORT: '0' },
  });
  child.unref();

  // Wait for the server to announce its port in the log file.
  const port = await waitForPort(logPath, 8000);
  if (!port) { console.error('server failed to start; see', logPath); process.exit(1); }

  const state = await readState();
  state[deck] = { port, pid: child.pid, log: logPath };
  await writeState(state);

  const url = `http://127.0.0.1:${port}/`;
  openBrowser(url);
  console.log(`launched → ${url}`);
}

function waitForPort(logPath, timeoutMs) {
  return new Promise((resolve) => {
    const start = Date.now();
    const iv = setInterval(() => {
      let txt = '';
      try { txt = fs.readFileSync(logPath, 'utf8'); } catch {}
      const m = txt.match(/SLIDES_VIZ_LISTENING (\d+)/);
      if (m) { clearInterval(iv); resolve(Number(m[1])); return; }
      if (Date.now() - start > timeoutMs) { clearInterval(iv); resolve(null); }
    }, 100);
  });
}

async function poll(deck) {
  const s = await sessionFor(deck);
  if (!s) { console.error('no active session for this deck. run: slides-viz launch ' + deck); process.exit(1); }
  const r = await get(s.port, '/__viz/poll'); // long-polls until feedback arrives
  const { items } = JSON.parse(r.body);
  if (!items || !items.length) { console.log('(no feedback)'); return; }
  // Human-readable for the agent's transcript.
  for (const it of items) {
    if (it.message === '__session_ended__') { console.log('SESSION ENDED by user.'); continue; }
    console.log('──────────────────────────────────────');
    if (it.time) console.log(`at: ${it.time} (video timecode)`);
    else console.log(`slide: ${it.slide ?? '(current)'}`);
    if (it.selector) console.log(`target: ${it.selector}`);
    if (it.snippet) console.log(`snippet: ${it.snippet}`);
    console.log(`message: ${it.message}`);
  }
  console.log('──────────────────────────────────────');
  // Machine-readable too, for good measure.
  console.log('JSON: ' + JSON.stringify(items));
}

async function end(deck) {
  const s = await sessionFor(deck);
  if (!s) { console.log('no active session.'); return; }
  try { await post(s.port, '/__viz/end', {}); } catch {}
  const state = await readState();
  delete state[deck];
  await writeState(state);
  console.log('session ended.');
}

async function status(deck) {
  const s = await sessionFor(deck);
  if (!s) { console.log('no active session for ' + deck); return; }
  console.log(`active → http://127.0.0.1:${s.port}/  (pid ${s.pid})`);
}

async function main() {
  const [cmd, file, kind] = process.argv.slice(2);
  if (!cmd || !file) usage();
  const deck = path.resolve(file);
  // `new` and `launch` create the file when missing; everything else needs it.
  const mayCreate = cmd === 'new' || cmd === 'launch';
  if (!mayCreate && cmd !== 'status' && cmd !== 'end' && !fs.existsSync(deck)) {
    console.error('deck file not found: ' + deck); process.exit(1);
  }
  if (cmd === 'new') return newDeck(deck, kind);
  if (cmd === 'launch') return launch(deck, kind);
  if (cmd === 'poll') return poll(deck);
  if (cmd === 'end') return end(deck);
  if (cmd === 'status') return status(deck);
  usage();
}
main().catch((e) => { console.error(e.message); process.exit(1); });
