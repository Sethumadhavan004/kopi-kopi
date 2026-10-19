import {Img, staticFile, useCurrentFrame} from 'remotion';
import {Look} from '../theme';
import {useTheme} from '../themes';

const SIZE = 128; // exported frame size
const HOT = 4; // the arrow's tip sits at (4, 4) in every frame
const LOOP = 48; // frames per animation loop

// The same polygon as ARROW in kopi_kopi/cursor_art.py (32-unit grid), scaled to 128 px.
const ARROW = [[1, 1], [1, 21], [6, 16.5], [9.5, 24.5], [13, 23], [9.5, 15], [16, 15]]
  .map(([x, y]) => `${x * 4},${y * 4}`)
  .join(' ');

/** A cursor whose tip (hotspot) is at (x, y). The galaxy PNGs are identical in both themes. */
export const Cursor: React.FC<{x: number; y: number; look: Look; scale?: number; opacity?: number}> = ({
  x,
  y,
  look,
  scale = 1,
  opacity = 1,
}) => {
  const frame = useCurrentFrame();
  const T = useTheme();
  const box: React.CSSProperties = {
    position: 'absolute',
    left: x - HOT * scale,
    top: y - HOT * scale,
    width: SIZE * scale,
    height: SIZE * scale,
    opacity,
  };
  if (look === 'plain') {
    return (
      <svg viewBox={`0 0 ${SIZE} ${SIZE}`} style={box}>
        <polygon points={ARROW} fill={T.cursor.fill} stroke={T.cursor.stroke} strokeWidth={5} strokeLinejoin="round" />
      </svg>
    );
  }
  const i = String(((frame % LOOP) + LOOP) % LOOP).padStart(2, '0');
  return (
    <div style={box}>
      {/* soft violet glow behind the galaxy */}
      <div
        style={{
          position: 'absolute',
          left: -60 * scale,
          top: -60 * scale,
          width: 220 * scale,
          height: 220 * scale,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${T.cursor.glow} 0%, transparent 65%)`,
        }}
      />
      <Img src={staticFile(`cursor-frames/${look}-arrow/${i}.png`)} style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}} />
    </div>
  );
};
