import {random} from 'remotion';

// A long, believable build/server log. Deterministic, so every render matches.
const MSGS = [
  'compiling src/auth/session.ts',
  'resolved 214 packages in 1.8s',
  'GET /api/orders 200 41ms',
  'cache miss user:4821',
  'worker 3 picked job #10442',
  'POST /api/checkout 201 88ms',
  'retrying db connection (2/5)',
  'bundle main.js 412 kB',
  'migrations up to date',
  'GET /api/health 200 3ms',
  'slow query orders_by_day 1.2s',
  'test users.spec: creates account',
  'test cart.spec: applies coupon',
  'webhook delivered evt_93fa',
  'gc pause 14ms',
];
const LEVELS = ['INFO', 'INFO', 'INFO', 'DEBUG', 'INFO', 'WARN', 'INFO', 'ERROR'];

export type LogLine = {n: number; time: string; level: string; msg: string};

export const LOG: LogLine[] = Array.from({length: 320}, (_, i) => {
  const s = 31 + i * 0.37;
  const time = `12:04:${String(Math.floor(s) % 60).padStart(2, '0')}.${String(
    Math.floor(random(`t${i}`) * 1000),
  ).padStart(3, '0')}`;
  return {
    n: i + 1,
    time,
    level: LEVELS[Math.floor(random(`l${i}`) * LEVELS.length)],
    msg: MSGS[Math.floor(random(`m${i}`) * MSGS.length)],
  };
});

export const lineText = (l: LogLine) => `${l.time}  ${l.level.padEnd(5)}  ${l.msg}`;
