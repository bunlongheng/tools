import chalk from 'chalk';

export const COLORS = {
  orange: '#D4694F', red: '#FF4444', green: '#98C379',
  blue: '#61AFEF', purple: '#C678DD', cyan: '#56B6C2',
  yellow: '#E5C07B', pink: '#FF79C6', teal: '#1ABC9C',
  lime: '#A8FF3E', indigo: '#7B6FBF', crimson: '#E06C75',
};

export const resolveColor = (input = 'orange') => {
  const s = String(input).toLowerCase().trim();
  return COLORS[s] ?? (s.startsWith('#') ? s : COLORS.orange);
};

export function parseColorArg(argv = process.argv.slice(2)) {
  for (let i = 0; i < argv.length; i++) {
    const m = argv[i].match(/^(?:--|\?)color=(.+)$/i);
    if (m) return m[1];
    if (/^--color$/i.test(argv[i]) && argv[i + 1]) return argv[i + 1];
  }
  return null;
}

// ── Mascot pixel art ──────────────────────────────────────────────────────
// H = accent (purple), B = body (user color)
// * = sparkle ✦, | = stem │, space = transparent
// All rows must be exactly 9 characters wide

export const MASCOTS = {

  claude: { label: 'Claude', art: [
    '    *    ',
    '    |    ',
    '  HHHHH  ',
    '  HHHHH  ',
    '  HHHHH  ',
    '  HHHHH  ',
    ' BBBBBBB ',
    ' BB   BB ',
    ' BBBBBBB ',
    '  BB BB  ',
    '  BB BB  ',
  ]},

  robo: { label: 'Robo', art: [    // classic boxy robot
    '   B B   ',
    '   B B   ',
    ' BBBBBBB ',
    ' B HHH B ',   // purple visor strip
    ' B     B ',
    ' BBBBBBB ',
    'BBBBBBBBB',   // wide shoulders
    ' B H H B ',   // purple control buttons
    ' BBBBBBB ',
    '  BB BB  ',
    '  BB BB  ',
  ]},

  kitty: { label: 'Kitty', art: [  // cat bot
    'BB     BB',   // pointy cat ears
    'BBB   BBB',
    'BBBBBBBBB',
    ' B H H B ',   // glowing cat eyes
    ' BBB BBB ',   // cheek puffs
    ' BBBBBBB ',
    ' BBBBBBB ',
    '  BBBBB  ',
    ' BBBBBBB ',
    '  BB BB  ',
    '  BB BB  ',
  ]},

  wizard: { label: 'Wizard', art: [ // tall wizard hat
    '    H    ',
    '   HHH   ',
    '  HHHHH  ',
    'HHHHHHHHH',   // wide hat brim
    ' BBBBBBB ',
    ' B     B ',
    ' BBBBBBB ',
    '  BBBBB  ',
    ' BBBBBBB ',
    'BBBBBBBBB',
    '  B   B  ',   // robe split
  ]},

  alien: { label: 'Alien', art: [   // big oval head alien
    ' H     H ',   // glowing antenna tips
    '  B   B  ',   // antenna stalks
    '  BBBBB  ',
    ' BBBBBBB ',
    ' B H H B ',   // huge purple eyes
    ' BBBBBBB ',
    '  BBBBB  ',
    '   BBB   ',   // thin neck
    ' BBBBBBB ',
    '  BB BB  ',
    '  BB BB  ',
  ]},

  owl: { label: 'Owl', art: [       // round owl with big eyes
    ' HH   HH ',   // ear tufts
    ' BBBBBBB ',
    'BBBBBBBBB',
    'BHHBBBHHB',   // two big round eyes
    'BHHBBBHHB',
    'BBBBBBBBB',
    '   BBB   ',   // beak
    '  BBBBB  ',
    ' BBBBBBB ',
    'BBBBBBBBB',
    ' BB   BB ',   // talons
  ]},

  ghost: { label: 'Ghost', art: [   // floating ghost
    '  BBBBB  ',
    ' BBBBBBB ',
    'BBBBBBBBB',
    ' B H H B ',   // spooky eyes
    'BBBBBBBBB',
    'BBBBBBBBB',
    ' BB B BB ',   // wavy underside
    ' B     B ',
    '         ',   // floating gap
    '    H    ',   // glow beneath
    '         ',
  ]},

  ninja: { label: 'Ninja', art: [   // masked ninja
    '  BBBBB  ',
    ' BBBBBBB ',
    'BBBBBBBBB',
    'HHHHHHHHH',   // purple headband
    'BBBBBBBBB',   // mask
    ' B H H B ',   // eyes through mask
    'BBBBBBBBB',
    '  BBBBB  ',
    ' BBBBBBB ',
    '  B   B  ',
    '  B   B  ',
  ]},

  astro: { label: 'Astro', art: [   // astronaut helmet
    '  HHHHH  ',
    ' HHHHHHH ',
    'HHHHHHHHH',
    'HH BBB HH',   // face inside visor
    'HH BBB HH',
    'HHHHHHHHH',
    ' BBBBBBB ',   // spacesuit
    ' B H H B ',   // suit controls
    'BBBBBBBBB',
    '  BB BB  ',
    '  BB BB  ',
  ]},

  knight: { label: 'Knight', art: [ // full plate armor
    '  BBBBB  ',
    ' BBBBBBB ',
    'BBBBBBBBB',
    ' B HHH B ',   // visor slit
    'BBBBBBBBB',
    '  BBBBB  ',   // gorget
    'BBBBBBBBB',   // pauldrons
    ' BBBBBBB ',
    ' B HHH B ',   // chest crest
    ' BBBBBBB ',
    '  BB BB  ',
  ]},

  pirate: { label: 'Pirate', art: [ // pirate captain
    'HHHHHHHHH',   // pirate hat
    'HHH   HHH',   // hat detail
    'HHHHHHHHH',
    ' BBBBBBB ',
    ' B HHH B ',   // eye patch + face
    ' BBBBBBB ',
    '  BBBBB  ',   // beard
    ' BBBBBBB ',
    'BBBBBBBBB',   // coat
    ' BB   BB ',
    '  BB BB  ',
  ]},

  devil: { label: 'Devil', art: [   // devil with horns
    'HH     HH',   // horn tips
    'HBH   HBH',   // horn bases (body+accent)
    'BBBBBBBBB',
    ' BBBBBBB ',
    ' B H H B ',   // glowing eyes
    ' BBBBBBB ',
    'BBBBBBBBB',
    ' BBBBBBB ',
    ' B     B ',
    ' BBBBBBB ',
    '  BB BB  ',
  ]},
};

const MASCOT_ACCENT = '#9B72CF';

export function renderMascot(mascotKey = 'claude', bodyColor = 'orange') {
  const mascot = MASCOTS[mascotKey] ?? MASCOTS.claude;
  const bc  = chalk.hex(resolveColor(bodyColor));
  const hat = chalk.hex(MASCOT_ACCENT);
  return mascot.art.map(row =>
    [...row].map(ch => {
      if (ch === 'H') return hat('█');
      if (ch === 'B') return bc('█');
      if (ch === '*') return chalk.hex(MASCOT_ACCENT)('✦');
      if (ch === '|') return chalk.dim('│');
      return ' ';
    }).join('')
  );
}

export function centeredMascot(mascotKey = 'claude', bodyColor = 'orange', panelWidth = 38) {
  const pad = ' '.repeat(Math.floor((panelWidth - 9) / 2));
  return renderMascot(mascotKey, bodyColor).map(l => pad + l);
}

// ── Banner layout ──────────────────────────────────────────────────────────
const visLen  = (s) => s.replace(/\x1b\[[0-9;]*m/g, '').length;
const padEnd_ = (s, n) => s + ' '.repeat(Math.max(0, n - visLen(s)));

export function createBanner({
  title = '', version = '', leftLines = [], sections = [],
  width = 80, leftWidth = 32, theme = {},
}) {
  const t = {
    border:    chalk.hex('#D4694F'),
    titleHi:   chalk.hex('#D4694F').bold,
    titleLo:   chalk.white,
    secHeader: chalk.hex('#D4694F').bold,
    content:   chalk.white,
    sep:       chalk.dim,
    ...theme,
  };
  const L = leftWidth, R = width - L - 5;
  const label = (title ? t.titleHi(title) : '') + (version ? t.titleLo(' ' + version) : '');
  const fill  = Math.max(0, L - visLen(label));
  const top   = t.border('╭─') + label + t.border('─'.repeat(fill) + '┬' + '─'.repeat(R + 1) + '╮');

  const rLines = [];
  sections.forEach((sec, i) => {
    if (i > 0) rLines.push(t.sep('─'.repeat(R)));
    rLines.push(t.secHeader(sec.header));
    sec.lines.forEach(l => rLines.push(t.content(l)));
  });

  const rows = Array.from(
    { length: Math.max(leftLines.length, rLines.length) },
    (_, i) =>
      t.border('│') + ' ' + padEnd_(leftLines[i] ?? '', L) +
      t.border('│') + ' ' + padEnd_(rLines[i]    ?? '', R) +
      t.border('│')
  );

  const bottom = t.border('╰' + '─'.repeat(L + 1) + '┴' + '─'.repeat(R + 1) + '╯');
  return [top, ...rows, bottom].join('\n');
}

export const printBanner = (cfg) => console.log(createBanner(cfg));
