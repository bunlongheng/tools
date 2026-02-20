#!/usr/bin/env node
import chalk from 'chalk';
import { printBanner, centeredMascot, MASCOTS } from './banner.js';

// Your actual 12 agents from bheng2026.vercel.app/ai/agent
const AGENTS = [
  { id: '01', name: 'BLAZE',  color: '#ff3333', role: 'Manager · Architecture', status: 'online',  mascot: 'claude'  },
  { id: '02', name: 'VENUS',  color: '#ff8800', role: 'UI · Branding',           status: 'online',  mascot: 'kitty'   },
  { id: '03', name: 'ZAP',    color: '#ffdd00', role: 'Performance',             status: 'online',  mascot: 'robo'    },
  { id: '04', name: 'EARTH',  color: '#00ff00', role: 'Cleanup',                 status: 'standby', mascot: 'wizard'  },
  { id: '05', name: 'BLITZ',  color: '#0099ff', role: 'Code Quality',            status: 'online',  mascot: 'owl'     },
  { id: '06', name: 'PULSE',  color: '#9933ff', role: 'Automation',              status: 'standby', mascot: 'ninja'   },
  { id: '07', name: 'ARROW',  color: '#ff66cc', role: 'UX · QA',                 status: 'online',  mascot: 'ghost'   },
  { id: '08', name: 'SAND',   color: '#cc6633', role: 'Storage',                 status: 'standby', mascot: 'pirate'  },
  { id: '09', name: 'SHADOW', color: '#6a6a8a', role: 'Security',                status: 'online',  mascot: 'devil'   },
  { id: '10', name: 'SNOW',   color: '#c8d8f0', role: 'Docs',                    status: 'standby', mascot: 'astro'   },
  { id: '11', name: 'GRAY',   color: '#9a9aaa', role: 'Dashboard',               status: 'standby', mascot: 'knight'  },
  { id: '12', name: 'CYAN',   color: '#00d9ff', role: 'Metrics',                 status: 'online',  mascot: 'alien'   },
];

const W = 80, L = 32;

const statusDot = (s) => s === 'online'
  ? chalk.hex('#22c55e')('● online')
  : chalk.hex('#eab308')('● standby');

for (const { id, name, color, role, status, mascot } of AGENTS) {
  const c     = chalk.hex(color);
  const label = MASCOTS[mascot].label;

  printBanner({
    title:     name,
    version:   `· ${role}`,
    width:     W,
    leftWidth: L,
    theme: {
      border:    c,
      titleHi:   c.bold,
      secHeader: c.bold,
    },
    leftLines: [
      '',
      ...centeredMascot(mascot, color, L),
      '',
      chalk.dim(`  agent-${id}  `) + statusDot(status),
    ],
    sections: [
      {
        header: name,
        lines: [
          `Name:    ${c.bold(name)}`,
          `Role:    ${chalk.white(role)}`,
          `Color:   ${c(color)}`,
          `Status:  ${statusDot(status)}`,
          '',
          chalk.dim(`node run.js --agent=${name.toLowerCase()}`),
        ],
      },
    ],
  });
  console.log();
}
