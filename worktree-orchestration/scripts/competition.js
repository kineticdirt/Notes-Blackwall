const fs = require('fs');
const path = require('path');
const { z } = require('zod');

const {
  makeState,
  conservative,
  radical,
  pragmatist,
  securityFocused,
  performanceFocused,
  userExperience,
  GOOSE_RE
} = require('../src/sanitizers');

const strategies = [
  { id: 'conservative', fn: conservative },
  { id: 'radical', fn: radical },
  { id: 'pragmatist', fn: pragmatist },
  { id: 'security-focused', fn: securityFocused },
  { id: 'performance-focused', fn: performanceFocused },
  { id: 'user-experience', fn: userExperience }
];

const Spec = z.object({
  version: z.string(),
  targetRegex: z.string(),
  maxLen: z.number().int().positive()
});

function nowIso() {
  return new Date().toISOString();
}

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

function writeFileAtomic(p, content) {
  const tmp = `${p}.tmp-${process.pid}`;
  fs.writeFileSync(tmp, content, { encoding: 'utf8', mode: 0o600 });
  fs.renameSync(tmp, p);
}

function benchOne(fn, inputs, iterations = 2000) {
  const start = process.hrtime.bigint();
  for (let i = 0; i < iterations; i++) {
    const state = makeState();
    for (const s of inputs) fn(s, state);
  }
  const end = process.hrtime.bigint();
  const ns = Number(end - start);
  return { iterations, nsTotal: ns, nsPerIteration: ns / iterations };
}

function score({ testsPassRate, nsPerIteration }, allNsPerIteration) {
  // Pragmatic scoring (mirrors spirit of spec):
  // - tests: 0.30
  // - performance: 0.20 (normalized)
  // - peer review + code quality + innovation: placeholders for now (0.50) with neutral values
  const testsScore = 100 * testsPassRate;

  // performance normalization (z-score on nsPerIteration; lower is better)
  const mean = allNsPerIteration.reduce((a, b) => a + b, 0) / allNsPerIteration.length;
  const variance =
    allNsPerIteration.reduce((a, x) => a + (x - mean) * (x - mean), 0) / allNsPerIteration.length;
  const std = Math.sqrt(variance || 1);
  const z = (nsPerIteration - mean) / std;
  // Convert to 0..100 where faster => higher score. Clamp.
  const perfScore = Math.max(0, Math.min(100, 50 - 15 * z));

  const peerReviewScore = 75;
  const codeQualityScore = 75;
  const innovationScore = 75;

  const total =
    0.3 * testsScore +
    0.2 * perfScore +
    0.25 * peerReviewScore +
    0.15 * codeQualityScore +
    0.1 * innovationScore;

  return { testsScore, perfScore, peerReviewScore, codeQualityScore, innovationScore, total };
}

function runTestsQuick(fn) {
  // Minimal “test harness” for this R&D: validate output constraints for a set of adversarial inputs
  const inputs = [
    'Gmail (junobyte.net)_gmail.users.labels.list',
    'Gmail (junobyte.net)_gmail.users.settings.filters.create',
    'spaces and dots.like.this (and parens)',
    '.....',
    '',
    '__',
    'x'.repeat(500)
  ];

  const state = makeState();
  for (const s of inputs) {
    const out = fn(s, state);
    if (!GOOSE_RE.test(out)) return { pass: false, reason: 'regex-fail', input: s, output: out };
    if (out.length < 1 || out.length > 128) return { pass: false, reason: 'len-fail', input: s, output: out };
  }
  return { pass: true };
}

function main() {
  const spec = Spec.parse({ version: '2.0.0', targetRegex: '^[a-zA-Z0-9_-]{1,128}$', maxLen: 128 });

  const root = path.resolve(__dirname, '..', '..'); // workspace root
  const worktreesRoot = path.join(root, 'worktrees');
  const sharedCache = path.join(worktreesRoot, '.shared-cache');
  const allSolutionsDir = path.join(sharedCache, 'all-solutions');
  const critiquesDir = path.join(sharedCache, 'critiques');
  ensureDir(allSolutionsDir);
  ensureDir(critiquesDir);

  const inputs = [
    'Gmail (junobyte.net)_gmail.users.labels.list',
    'Gmail (junobyte.net)_gmail.users.settings.filters.create',
    'spaces and dots.like.this (and parens)',
    'x'.repeat(256),
    '.....',
    ''
  ];

  const results = [];
  for (const s of strategies) {
    const t = runTestsQuick(s.fn);
    const b = benchOne(s.fn, inputs, 2000);
    results.push({
      id: s.id,
      tests: t,
      perf: b
    });
  }

  const nsList = results.map((r) => r.perf.nsPerIteration);
  const scored = results.map((r) => {
    const testsPassRate = r.tests.pass ? 1 : 0;
    const scores = score({ testsPassRate, nsPerIteration: r.perf.nsPerIteration }, nsList);
    return { ...r, scores };
  });

  scored.sort((a, b) => b.scores.total - a.scores.total);
  const winner = scored[0];

  const report = [
    `# Competition report (tool-name sanitization)`,
    ``,
    `- Generated: ${nowIso()}`,
    `- Spec version: ${spec.version}`,
    `- Target regex: \`${spec.targetRegex}\``,
    ``,
    `## Leaderboard`,
    ...scored.map((r, i) => {
      const t = r.tests.pass ? 'PASS' : `FAIL (${r.tests.reason})`;
      return `- ${i + 1}. **${r.id}** — total=${r.scores.total.toFixed(2)} tests=${t} perf(ns/iter)=${r.perf.nsPerIteration.toFixed(0)}`;
    }),
    ``,
    `## Winner`,
    `**${winner.id}**`,
    ``,
    `## Notes`,
    `This is a pragmatic harness applying the worktree-orchestration spec to the current R&D blocker: Goose MCP tool-name validation.`,
    `Peer review / code quality / innovation are currently neutral placeholders; we can wire those to real cross-review and complexity metrics next.`,
    ``
  ].join('\n');

  writeFileAtomic(path.join(sharedCache, 'competition-report.md'), report);
  writeFileAtomic(path.join(allSolutionsDir, `results-${Date.now()}.json`), JSON.stringify(scored, null, 2));

  // eslint-disable-next-line no-console
  console.log(report);
}

main();

