// Turns the rendered demo into a README GIF: played at 2x so the whole demo fits in 6 s,
// 600 px wide, 15 fps, under 5 MB.
//   npm run render:demo && npm run gif
import {execFileSync} from 'node:child_process';
import {statSync} from 'node:fs';

const src = 'out/demo-frames.mp4';
const gif = 'out/kopi-kopi-demo.gif';
const fps = 15;
const width = 600;
const speed = 2;

// Two passes: build a 128-colour palette from the clip, then dither the clip with it.
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', src,
  '-vf', `setpts=PTS/${speed},fps=${fps},scale=${width}:-1:flags=lanczos,palettegen=max_colors=128:stats_mode=diff`, 'out/palette.png']);
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', src, '-i', 'out/palette.png',
  '-lavfi', `setpts=PTS/${speed},fps=${fps},scale=${width}:-1:flags=lanczos[v];[v][1:v]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle`, gif]);

const mb = statSync(gif).size / 1024 / 1024;
console.log(`wrote ${gif} (${mb.toFixed(2)} MB)${mb > 5 ? '  OVER 5 MB: lower fps or max_colors' : ''}`);
