# Banner — Terminal Banner Generator

> Reusable terminal banner with 12 pixel-art agents, each with their own color and character.

---

## Requirements

```bash
node --version   # v18+
```

## Setup

```bash
cd banner/
npm install
```

## Run All 12 Agents

```bash
node agents.js
```

## Use in Your Own Scripts

```js
import { printBanner, centeredMascot } from '../banner/banner.js';

printBanner({
  title:     'BLAZE',
  version:   '· Manager · Architecture',
  width:     80,
  leftWidth: 32,
  theme: {
    border:  chalk.hex('#ff3333'),
    titleHi: chalk.hex('#ff3333').bold,
  },
  leftLines: [
    '',
    ...centeredMascot('claude', '#ff3333', 32),
  ],
  sections: [
    { header: 'BLAZE', lines: ['Status: online'] },
  ],
});
```

## Color Parameter

```bash
node my-script.js --color=green
node my-script.js --color=#ff3333
node my-script.js ?color=cyan
```

## The 12 Agents

| Agent  | Color     | Role                  | Mascot  |
|--------|-----------|----------------------|---------|
| BLAZE  | `#ff3333` | Manager · Architecture | Claude  |
| VENUS  | `#ff8800` | UI · Branding          | Kitty   |
| ZAP    | `#ffdd00` | Performance            | Robo    |
| EARTH  | `#00ff00` | Cleanup                | Wizard  |
| BLITZ  | `#0099ff` | Code Quality           | Owl     |
| PULSE  | `#9933ff` | Automation             | Ninja   |
| ARROW  | `#ff66cc` | UX · QA                | Ghost   |
| SAND   | `#cc6633` | Storage                | Pirate  |
| SHADOW | `#6a6a8a` | Security               | Devil   |
| SNOW   | `#c8d8f0` | Docs                   | Astro   |
| GRAY   | `#9a9aaa` | Dashboard              | Knight  |
| CYAN   | `#00d9ff` | Metrics                | Alien   |

## Mascot Pixel Art

Each mascot is a 9×11 pixel grid defined in `banner.js`:

```
H = accent color (purple #9B72CF)
B = body color   (agent's color)
* = sparkle ✦
| = stem │
  = transparent
```

Swap any row in `MASCOTS` to customize a character.
