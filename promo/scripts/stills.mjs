// Renders key frames as PNGs and tiles them into one contact sheet per composition,
// to review before a full render. Bundles once, renders every composition from it.
//   node scripts/stills.mjs [Square-Hikari Wide-Ankoku ...]
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import {execFileSync} from 'node:child_process';
import {mkdirSync, rmSync} from 'node:fs';
import path from 'node:path';

const ALL = ['Square-Hikari', 'Square-Ankoku', 'Wide-Hikari', 'Wide-Ankoku'];
const ids = process.argv.slice(2).length ? process.argv.slice(2) : ALL;
const FRAMES = (process.env.FRAMES ?? '60,100,115,165,240,305,360,410,500,520,580,600,640,690,740,775')
  .split(',')
  .map(Number);

const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
for (const id of ids) {
  const composition = await selectComposition({serveUrl, id});
  const dir = path.resolve('out/stills', id);
  rmSync(dir, {recursive: true, force: true});
  mkdirSync(dir, {recursive: true});
  for (const [i, frame] of FRAMES.entries()) {
    await renderStill({composition, serveUrl, frame, output: path.join(dir, `s${String(i).padStart(2, '0')}.png`)});
  }
  // 4 across, each frame 480 px wide, frame number burned in the top-left
  const out = path.join('out', `contact-${id}.png`);
  execFileSync('ffmpeg', [
    '-y', '-loglevel', 'error', '-i', path.join(dir, 's%02d.png'),
    '-vf', `scale=480:-1,tile=4x${Math.ceil(FRAMES.length / 4)}:padding=8:color=0x888888`,
    '-frames:v', '1', out,
  ]);
  console.log('wrote', out);
}
