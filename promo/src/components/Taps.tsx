import {useCurrentFrame} from 'remotion';
import {kf} from '../theme';

/** A ring expanding from (x, y), `t` frames after it starts. */
const Ring: React.FC<{x: number; y: number; t: number; color: string; r0: number; r1: number; width?: number}> = ({
  x,
  y,
  t,
  color,
  r0,
  r1,
  width = 5,
}) => {
  if (t < 0 || t > 22) return null;
  const r = kf(t, [0, 20], [r0, r1]);
  const a = kf(t, [0, 3, 20], [0, 1, 0]);
  return <div style={{...dot(x, y, r, 'transparent', a), border: `${width}px solid ${color}`, boxShadow: `0 0 16px ${color}`}} />;
};

/** Expanding ripple rings at the tap point, in the step's colour. */
export const Ripple: React.FC<{x: number; y: number; at: number; color: string}> = ({x, y, at, color}) => {
  const t = useCurrentFrame() - at;
  return (
    <>
      <Ring x={x} y={y} t={t} color={color} r0={6} r1={52} />
      <Ring x={x} y={y} t={t - 6} color={color} r0={6} r1={80} width={3} />
    </>
  );
};

const dot = (x: number, y: number, r: number, bg: string, opacity: number): React.CSSProperties => ({
  position: 'absolute',
  left: x - r,
  top: y - r,
  width: 2 * r,
  height: 2 * r,
  borderRadius: '50%',
  background: bg,
  opacity,
});
