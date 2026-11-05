#!/usr/bin/env node
/*
 * canvas-page-check.js - headless geometry + data-shape check for a single-file canvas widget.
 *
 *   node canvas-page-check.js widget.html [--set id=value]... [--call "expr"]... [--expect N] [--frames N]
 *
 * Why: the page's own <script> is what draws, and a browser round-trip is the slowest way to learn
 * that a coordinate is NaN, a curve left the panel, or a label printed "NaN". This runs the widget's
 * script against recording canvas stubs and prints what it did. No browser, no network.
 *
 * Adapt these three things per widget:
 *   1. canvases are discovered from <canvas id="..." width="..." height="..."> in the markup, so give
 *      every canvas an id and set its size in attributes (never size from a DOM rect: a hidden tab's
 *      rect is 0 and blanks the canvas);
 *   2. the payload global for --expect probes DATA / SETS / RUNS / data / sets / runs / D - or expose
 *      yours with a --call expression;
 *   3. document.querySelector('.class') is not implemented (returns []), so prefer getElementById in
 *      the widget or reach the draw function through --call.
 *
 * It judges GEOMETRY and NUMBERS only. Appearance, colour, glyph collisions and legibility are a
 * render + vision pass; run both.
 */
'use strict';
const fs = require('fs');
const vm = require('vm');
const path = require('path');

const argv = process.argv.slice(2);
const file = argv[0];
if (!file || file.startsWith('--')) {
  console.error('usage: node canvas-page-check.js <widget.html> [--set id=value]... [--call "expr"]... [--expect N] [--frames N]');
  process.exit(2);
}
const opts = { sets: [], calls: [], expect: null, frames: 0 };
for (let i = 1; i < argv.length; i++) {
  const a = argv[i];
  if (a === '--set') { const p = String(argv[++i]).split('='); opts.sets.push([p[0], p.slice(1).join('=')]); }
  else if (a === '--call') opts.calls.push(argv[++i]);
  else if (a === '--expect') opts.expect = Number(argv[++i]);
  else if (a === '--frames') opts.frames = Number(argv[++i]);
  else console.error('ignoring unknown option ' + a);
}

const problems = [];
const notes = [];
const html = fs.readFileSync(file, 'utf8');
const NUMISH = /(NaN|Infinity|undefined)/;
const r2 = v => Math.round(v * 100) / 100;

/* ---- 1. canvases, sized from the markup -------------------------------- */
const canvases = new Map();
for (const m of html.matchAll(/<canvas\b[^>]*>/gi)) {
  const tag = m[0];
  const id = (tag.match(/\bid="([^"]+)"/) || [])[1];
  if (!id) { problems.push('a <canvas> in the markup has no id - it cannot be mapped or asserted'); continue; }
  canvases.set(id, {
    id, w: Number((tag.match(/\bwidth="(\d+)"/) || [])[1] || 300),
    h: Number((tag.match(/\bheight="(\d+)"/) || [])[1] || 150),
    calls: 0, tags: Object.create(null), box: [1e9, 1e9, -1e9, -1e9], dynamic: false,
  });
}
if (!canvases.size) problems.push('no <canvas id="..."> found - is this the widget file?');
notes.push('canvases: ' + ([...canvases.keys()].join(', ') || 'none'));

/* ---- 2. the widget's own script (inline, classic) ---------------------- */
const scripts = [...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)]
  .filter(m => !/\bsrc=/.test(m[1]) && !/type="(module|application\/json)"/.test(m[1]))
  .map(m => m[2]);
if (!scripts.length) problems.push('no inline <script> to run');

/* ---- 3. DOM stubs ------------------------------------------------------ */
let dynCount = 0;
const mkStyle = () => ({ setProperty() {}, removeProperty() {}, getPropertyValue() { return ''; } });

function ctxFor(cv) {
  const note = (tag, xs, ys) => {
    cv.calls++;
    cv.tags[tag] = (cv.tags[tag] || 0) + 1;
    for (const v of [].concat(xs, ys)) if (!Number.isFinite(v)) problems.push('non-finite coordinate in ' + tag + ' on #' + cv.id);
    const xf = xs.filter(Number.isFinite), yf = ys.filter(Number.isFinite);
    if (xf.length) { cv.box[0] = Math.min(cv.box[0], ...xf); cv.box[2] = Math.max(cv.box[2], ...xf); }
    if (yf.length) { cv.box[1] = Math.min(cv.box[1], ...yf); cv.box[3] = Math.max(cv.box[3], ...yf); }
  };
  const label = (t, x, y, tag) => {
    if (NUMISH.test(String(t))) problems.push('label built from a non-finite number on #' + cv.id + ': ' + String(t).slice(0, 60));
    note(tag, [x], [y]);
  };
  // an arc contributes +/- r to the extent, so a marker sitting on the panel edge can report a
  // few px of overflow - read the tag counts before chasing it.
  return {
    save() {}, restore() {}, beginPath() {}, closePath() {}, clip() {}, fill() {}, stroke() {},
    moveTo: (x, y) => note('moveTo', [x], [y]),
    lineTo: (x, y) => note('lineTo', [x], [y]),
    arc: (x, y, r) => note('arc', [x - r, x + r], [y - r, y + r]),
    rect: (x, y, w, h) => note('rect', [x, x + w], [y, y + h]),
    fillRect: (x, y, w, h) => note('fillRect', [x, x + w], [y, y + h]),
    strokeRect: (x, y, w, h) => note('strokeRect', [x, x + w], [y, y + h]),
    clearRect() {}, setLineDash() {}, setTransform() {}, translate() {}, rotate() {}, scale() {},
    fillText: (t, x, y) => label(t, x, y, 'fillText'),
    strokeText: (t, x, y) => label(t, x, y, 'strokeText'),
    measureText: t => ({ width: String(t).length * 7 }),
    createLinearGradient: () => ({ addColorStop() {} }),
    createRadialGradient: () => ({ addColorStop() {} }),
    createPattern: () => null, drawImage() {}, putImageData() {},
    getImageData: (x, y, w, h) => ({ data: new Uint8ClampedArray(Math.max(4, Math.floor(w * h) * 4)) }),
    font: '', fillStyle: '#000', strokeStyle: '#000', lineWidth: 1, globalAlpha: 1,
    textAlign: 'start', textBaseline: 'alphabetic', lineCap: 'butt', lineJoin: 'miter', globalCompositeOperation: 'source-over',
  };
}

function el(tag, id) {
  const e = {
    tagName: String(tag || 'div').toUpperCase(), id, value: '', textContent: '', innerHTML: '', text: '',
    checked: false, disabled: false, hidden: false, width: 300, height: 150,
    style: mkStyle(), dataset: {}, children: [], childNodes: [], firstChild: null, lastChild: null,
    classList: {
      _s: new Set(),
      add(...c) { c.forEach(x => this._s.add(x)); }, remove(...c) { c.forEach(x => this._s.delete(x)); },
      toggle(c, f) { (f === undefined ? !this._s.has(c) : f) ? this._s.add(c) : this._s.delete(c); },
      contains(c) { return this._s.has(c); },
    },
    addEventListener() {}, removeEventListener() {}, dispatchEvent() { return true; },
    appendChild(c) { this.children.push(c); this.firstChild = this.children[0]; this.lastChild = c; return c; },
    insertBefore(c) { this.children.push(c); return c; }, removeChild() {}, remove() {},
    setAttribute(k, v) { this[k] = v; }, getAttribute(k) { return this[k] === undefined ? null : this[k]; },
    querySelector() { return null; }, querySelectorAll() { return []; },
    getBoundingClientRect() { return { x: 0, y: 0, left: 0, top: 0, width: this.width, height: this.height, right: this.width, bottom: this.height }; },
    focus() {}, blur() {}, click() {}, scrollIntoView() {}, insertAdjacentHTML() {},
    cloneNode() { return el(tag, id); }, getContext() { return null; },
  };
  return e;
}

const els = new Map();
for (const cv of canvases.values()) {
  const e = el('canvas', cv.id);
  e.width = cv.w; e.height = cv.h;
  e.getContext = () => (e.__ctx = e.__ctx || ctxFor(cv));
  els.set(cv.id, e);
}
const byId = id => {
  if (!els.has(id)) els.set(id, el('div', id));
  return els.get(id);
};
function newCanvasEl() {
  const cv = { id: 'dynamic-' + (++dynCount), w: 300, h: 150, calls: 0, tags: Object.create(null), box: [1e9, 1e9, -1e9, -1e9], dynamic: true };
  const e = el('canvas', cv.id);
  e.getContext = () => (e.__ctx = e.__ctx || ctxFor(cv));
  return e;
}

const raf = [], timeouts = [];
const sandbox = {
  console, Math, JSON, Date, Number, String, Boolean, Array, Object, Set, Map, Promise, Error, Symbol,
  isNaN, isFinite, parseFloat, parseInt, Uint8ClampedArray, Float64Array, Int32Array,
  requestAnimationFrame: cb => { raf.push(cb); return raf.length; },
  cancelAnimationFrame() {},
  setTimeout: f => { timeouts.push(f); return 0; }, clearTimeout() {}, setInterval: () => 0, clearInterval() {},
  performance: { now: () => Date.now() },
  devicePixelRatio: 1,
  matchMedia: () => ({ matches: false, addEventListener() {}, addListener() {} }),
  getComputedStyle: () => ({ getPropertyValue: () => '', color: '', backgroundColor: '' }),
  navigator: { userAgent: 'node/canvas-page-check' },
  location: { href: 'file://' + path.resolve(file) },
  alert() {}, prompt: () => null,
  document: {
    getElementById: byId,
    querySelector: sel => (sel && sel[0] === '#' ? byId(sel.slice(1)) : null),
    querySelectorAll: sel => (sel === 'canvas' ? [...canvases.values()].map(cv => els.get(cv.id)) : []),
    createElement: t => (String(t).toLowerCase() === 'canvas' ? newCanvasEl() : el(t)),
    addEventListener() {}, removeEventListener() {},
    body: el('body'), head: el('head'), documentElement: el('html'),
  },
};
sandbox.window = sandbox;
sandbox.globalThis = sandbox;

/* ---- 4. run it --------------------------------------------------------- */
for (const [id, v] of opts.sets) byId(id).value = v;
let threw = false;
try {
  vm.createContext(sandbox);
  vm.runInContext(scripts.join('\n;\n'), sandbox, { filename: path.basename(file) });
} catch (e) {
  threw = true;
  problems.push('the widget script threw: ' + e.message + '\n      ' + String(e.stack).split('\n').slice(0, 4).join('\n      '));
}
if (!threw) {
  for (const expr of opts.calls) {
    try { vm.runInContext(expr, sandbox, { timeout: 5000 }); }
    catch (e) { problems.push('--call "' + expr + '" threw: ' + e.message); }
  }
  notes.push('probe hook: ' + (sandbox.__w ? 'window.__w = {' + Object.keys(sandbox.__w).join(', ') + '}' : 'NOT defined - a parse error or a body that never ran'));
}

/* ---- 5. pump animation frames (optional) ------------------------------- */
let t = 0;
for (let f = 0; f < opts.frames; f++) {
  const q = raf.splice(0, raf.length);
  t += 16.7;
  for (const cb of q) { try { cb(t); } catch (e) { problems.push('frame ' + f + ' threw: ' + e.message); } }
  for (const fn of timeouts.splice(0, timeouts.length)) { try { fn(); } catch (e) { problems.push('a timeout threw: ' + e.message); } }
}
if (opts.frames && !raf.length) notes.push('no requestAnimationFrame callback was queued - the animate loop may not be running');

/* ---- 6. assertions and report ------------------------------------------ */
if (opts.expect !== null) {
  let got = null, name = null;
  for (const k of ['DATA', 'SETS', 'RUNS', 'data', 'sets', 'runs', 'D']) {
    if (Array.isArray(sandbox[k])) { got = sandbox[k].length; name = k; break; }
  }
  if (got === null) problems.push('--expect was given but no array payload (DATA/SETS/RUNS/...) is visible in page scope - expose one with --call or the probe hook');
  else if (got !== opts.expect) problems.push('payload ' + name + ' has ' + got + ' entries, expected ' + opts.expect);
  else notes.push('payload ' + name + ': ' + got + ' entries (expected ' + opts.expect + ')');
}
for (const cv of canvases.values()) {
  const [x0, y0, x1, y1] = cv.box;
  if (!cv.calls) { problems.push('#' + cv.id + ' recorded no draw calls - the draw function never ran, or drew nothing'); continue; }
  const top = Object.entries(cv.tags).sort((a, b) => b[1] - a[1]).slice(0, 4).map(x => x[0] + ' x' + x[1]).join(', ');
  if (cv.dynamic) { notes.push('#' + cv.id + ' (offscreen): ' + cv.calls + ' calls'); continue; }
  if (x0 < -2 || y0 < -2 || x1 > cv.w + 2 || y1 > cv.h + 2) {
    problems.push('#' + cv.id + ' draws outside its box: x [' + r2(x0) + ',' + r2(x1) + '] y [' + r2(y0) + ',' + r2(y1) + '] vs ' + cv.w + 'x' + cv.h + ' (top calls: ' + top + ')');
  } else {
    notes.push('#' + cv.id + ': ' + cv.calls + ' calls, x [' + r2(x0) + ',' + r2(x1) + '] y [' + r2(y0) + ',' + r2(y1) + '] inside ' + cv.w + 'x' + cv.h + ' (top: ' + top + ')');
  }
}

for (const n of notes) console.log('  - ' + n);
if (problems.length) {
  console.log('\nFAIL - ' + problems.length + ' problem(s):');
  for (const p of problems) console.log('  ! ' + p);
  process.exit(1);
}
console.log('\nPASS - script ran, ' + canvases.size + ' canvas(es) drawn inside their boxes, no non-finite geometry');
