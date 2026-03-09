const crypto = require('crypto');

const GOOSE_RE = /^[a-zA-Z0-9_-]{1,128}$/;

function shortHash(s, n = 10) {
  return crypto.createHash('sha256').update(String(s)).digest('hex').slice(0, n);
}

function ensureValidOrThrow(name) {
  if (!GOOSE_RE.test(name)) {
    throw new Error(`Sanitized name is invalid: ${JSON.stringify(name)}`);
  }
  return name;
}

// Conservative: simple regex replace + collapse + stable suffix when needed.
function conservative(original, state) {
  let base = String(original).replace(/[^a-zA-Z0-9_-]+/g, '_').replace(/_+/g, '_').replace(/^_+|_+$/g, '');
  if (!base) base = 'tool';

  const suffix = shortHash(original, 10);
  if (base.length > 128) base = `${base.slice(0, 128 - 1 - suffix.length)}_${suffix}`;

  const existing = state.used.get(base);
  if (existing && existing !== original) {
    base = `${base.slice(0, 128 - 1 - suffix.length)}_${suffix}`;
  }

  state.used.set(base, original);
  return ensureValidOrThrow(base);
}

// Radical: functional pipeline + deliberate novelty bonus hook (still deterministic).
function radical(original, state) {
  const s = String(original);
  const cleaned = Array.from(s)
    .map((ch) => (/[a-zA-Z0-9_-]/.test(ch) ? ch : '_'))
    .join('')
    .replace(/_+/g, '_')
    .replace(/^_+|_+$/g, '');

  const base0 = cleaned || 'tool';
  const suffix = shortHash(`radical:${s}`, 12);
  let base = base0.length > 128 ? `${base0.slice(0, 128 - 1 - suffix.length)}_${suffix}` : base0;

  if (state.used.has(base) && state.used.get(base) !== s) {
    base = `${base.slice(0, 128 - 1 - suffix.length)}_${suffix}`;
  }
  state.used.set(base, s);
  return ensureValidOrThrow(base);
}

// Pragmatist: keep as much as possible, only fix invalid chars; small suffix on collision.
function pragmatist(original, state) {
  const s = String(original);
  let base = s.replace(/[^a-zA-Z0-9_-]/g, '_');
  if (!base) base = 'tool';
  base = base.replace(/_+/g, '_').replace(/^_+|_+$/g, '');
  if (!base) base = 'tool';

  if (base.length > 128) {
    const suffix = shortHash(s, 8);
    base = `${base.slice(0, 128 - 1 - suffix.length)}_${suffix}`;
  }

  if (state.used.has(base) && state.used.get(base) !== s) {
    const suffix = shortHash(`p:${s}`, 10);
    base = `${base.slice(0, 128 - 1 - suffix.length)}_${suffix}`;
  }
  state.used.set(base, s);
  return ensureValidOrThrow(base);
}

// Security-focused: strict canonicalization + guaranteed uniqueness via hash suffix always.
function securityFocused(original, state) {
  const s = String(original);
  const canonical = s.normalize('NFKC');
  let base = canonical.replace(/[^a-zA-Z0-9_-]+/g, '_').replace(/_+/g, '_').replace(/^_+|_+$/g, '');
  if (!base) base = 'tool';
  const suffix = shortHash(`sec:${canonical}`, 16);

  // Always include a suffix to avoid accidental collisions and to be explicit.
  if (base.length > 128 - 1 - suffix.length) {
    base = base.slice(0, 128 - 1 - suffix.length);
  }
  base = `${base}_${suffix}`;

  // If still colliding (extremely unlikely), extend hash.
  let extra = 18;
  while (state.used.has(base) && state.used.get(base) !== s && extra <= 28) {
    const sfx = shortHash(`sec:${canonical}`, extra);
    let prefix = base.split('_').slice(0, -1).join('_') || 'tool';
    if (prefix.length > 128 - 1 - sfx.length) prefix = prefix.slice(0, 128 - 1 - sfx.length);
    base = `${prefix}_${sfx}`;
    extra += 2;
  }

  state.used.set(base, s);
  return ensureValidOrThrow(base);
}

// Performance-focused: single-pass sanitizer (no regex in main loop) + suffix on collision/overflow.
function performanceFocused(original, state) {
  const s = String(original);
  let out = '';
  let lastUnderscore = false;
  for (let i = 0; i < s.length; i++) {
    const code = s.charCodeAt(i);
    const isAZ = code >= 65 && code <= 90;
    const isaz = code >= 97 && code <= 122;
    const is09 = code >= 48 && code <= 57;
    const isOK = isAZ || isaz || is09 || code === 95 || code === 45; // _ or -
    if (isOK) {
      out += s[i];
      lastUnderscore = false;
    } else if (!lastUnderscore) {
      out += '_';
      lastUnderscore = true;
    }
    if (out.length > 160) break; // cap intermediate growth
  }
  out = out.replace(/_+/g, '_').replace(/^_+|_+$/g, '');
  if (!out) out = 'tool';

  const suffix = shortHash(`perf:${s}`, 10);
  if (out.length > 128) out = `${out.slice(0, 128 - 1 - suffix.length)}_${suffix}`;

  if (state.used.has(out) && state.used.get(out) !== s) {
    out = `${out.slice(0, 128 - 1 - suffix.length)}_${suffix}`;
  }
  state.used.set(out, s);
  return ensureValidOrThrow(out);
}

// UX: prioritize readability (shorten domain-ish bits) + keep stable.
function userExperience(original, state) {
  const s = String(original);
  // Heuristic: collapse parenthetical provider fragments like "(junobyte.net)" -> "junobyte_net"
  const simplified = s.replace(/\(([^)]+)\)/g, (_, inner) => `_${inner}_`);
  let base = simplified
    .replace(/[^a-zA-Z0-9_-]+/g, '_')
    .replace(/_+/g, '_')
    .replace(/^_+|_+$/g, '');
  if (!base) base = 'tool';

  // Prefer keeping it short and scannable; add suffix only if needed.
  if (base.length > 96) {
    const suffix = shortHash(`ux:${s}`, 8);
    base = `${base.slice(0, 96 - 1 - suffix.length)}_${suffix}`;
  }

  if (base.length > 128) {
    const suffix = shortHash(`ux:${s}`, 10);
    base = `${base.slice(0, 128 - 1 - suffix.length)}_${suffix}`;
  }

  if (state.used.has(base) && state.used.get(base) !== s) {
    const suffix = shortHash(`ux:${s}`, 10);
    base = `${base.slice(0, 128 - 1 - suffix.length)}_${suffix}`;
  }
  state.used.set(base, s);
  return ensureValidOrThrow(base);
}

function makeState() {
  return { used: new Map() };
}

module.exports = {
  GOOSE_RE,
  makeState,
  conservative,
  radical,
  pragmatist,
  securityFocused,
  performanceFocused,
  userExperience
};

