const Benchmark = require('benchmark');

const {
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

const samples = [
  'Gmail (junobyte.net)_gmail.users.labels.list',
  'Gmail (junobyte.net)_gmail.users.settings.filters.create',
  'spaces and dots.like.this (and parens)',
  'x'.repeat(256),
  'x'.repeat(64) + ' (provider.net)_x.y.z',
  '.....',
  ''
];

const suite = new Benchmark.Suite();

for (const [name, fn] of Object.entries(strategies)) {
  suite.add(name, function () {
    const state = makeState();
    for (const s of samples) fn(s, state);
  });
}

suite
  .on('cycle', function (event) {
    // eslint-disable-next-line no-console
    console.log(String(event.target));
  })
  .on('complete', function () {
    // eslint-disable-next-line no-console
    console.log('Fastest is ' + this.filter('fastest').map('name'));
  })
  .run({ async: false });

