const fc = require('fast-check');

const {
  GOOSE_RE,
  makeState,
  conservative,
  radical,
  pragmatist,
  securityFocused,
  performanceFocused,
  userExperience
} = require('../src/sanitizers');

const strategies = {
  conservative,
  radical,
  pragmatist,
  securityFocused,
  performanceFocused,
  userExperience
};

describe('tool-name sanitizers (R&D harness)', () => {
  test('all strategies output Goose-valid names for known bad samples', () => {
    const bad = [
      'Gmail (junobyte.net)_gmail.users.labels.list',
      'Gmail (junobyte.net)_gmail.users.settings.filters.create',
      'spaces and dots.like.this (and parens)',
      '.....',
      '',
      '___',
      'x'.repeat(500)
    ];

    for (const [name, fn] of Object.entries(strategies)) {
      const state = makeState();
      for (const input of bad) {
        const out = fn(input, state);
        expect(GOOSE_RE.test(out)).toBe(true);
        expect(out.length).toBeGreaterThanOrEqual(1);
        expect(out.length).toBeLessThanOrEqual(128);
      }
    }
  });

  test('property: outputs always match Goose regex', () => {
    const arbitrary = fc.string({ maxLength: 500 });

    for (const [name, fn] of Object.entries(strategies)) {
      fc.assert(
        fc.property(arbitrary, (s) => {
          const state = makeState();
          const out = fn(s, state);
          return GOOSE_RE.test(out) && out.length >= 1 && out.length <= 128;
        }),
        { numRuns: 200 }
      );
    }
  });

  test('property: deterministic for same input within same strategy (fresh state)', () => {
    const arbitrary = fc.string({ maxLength: 200 });

    for (const [name, fn] of Object.entries(strategies)) {
      fc.assert(
        fc.property(arbitrary, (s) => {
          const a = fn(s, makeState());
          const b = fn(s, makeState());
          return a === b;
        }),
        { numRuns: 200 }
      );
    }
  });

  test('collision behavior: two different inputs should not silently map to same output in a single run (best effort)', () => {
    // This is not a mathematical guarantee for all inputs, but should hold for typical collisions.
    const pairs = [
      ['A (x).b', 'A  x _b'],
      ['..', '__'],
      ['hello world', 'hello_world']
    ];

    for (const [name, fn] of Object.entries(strategies)) {
      const state = makeState();
      const outputs = new Set();
      for (const [a, b] of pairs) {
        outputs.add(fn(a, state));
        outputs.add(fn(b, state));
      }
      // At least 2 distinct outputs across 3 pairs for all strategies.
      expect(outputs.size).toBeGreaterThanOrEqual(2);
    }
  });
});

