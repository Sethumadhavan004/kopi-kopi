import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {kf, pop} from '../theme';
import {Hue, useTheme} from '../themes';

// HIKARI's six forms, drifting slowly behind a scene. Moving, never busy.
export type Form = 'sun' | 'dawn' | 'peak' | 'tile' | 'orbit' | 'voice';
export type ShapeSpec = {form: Form; x: number; y: number; size: number; hue: Hue; phase?: number};

export const INFINITY = 'M14 30 C 14 10, 40 10, 60 30 S 106 50, 106 30 S 80 10, 60 30 S 14 50, 14 30 Z';

const Shape: React.FC<{form: Form; color: string; spin: number}> = ({form, color, spin}) => {
  switch (form) {
    case 'sun':
      return <circle cx="50" cy="50" r="50" fill={color} />;
    case 'dawn':
      return <path d="M0 62 A50 50 0 0 1 100 62 Z" fill={color} />;
    case 'peak':
      return <polygon points="50,10 92,86 8,86" fill={color} stroke={color} strokeWidth="10" strokeLinejoin="round" />;
    case 'tile':
      return <rect x="12" y="12" width="76" height="76" rx="18" fill={color} transform="rotate(18 50 50)" />;
    case 'orbit':
      return (
        <circle cx="50" cy="50" r="44" fill="none" stroke={color} strokeWidth="6" strokeDasharray="10 9" strokeLinecap="round" transform={`rotate(${spin} 50 50)`} />
      );
    case 'voice':
      return (
        <g transform="translate(0 25) scale(0.8333)">
          <path d={INFINITY} fill="none" stroke={color} strokeWidth="9" strokeLinejoin="round" />
        </g>
      );
  }
};

/** Floating forms. x and y are fractions of the frame; shapes may overlap the edges on purpose. */
export const Shapes: React.FC<{items: ShapeSpec[]; at?: number}> = ({items, at = 0}) => {
  const f = useCurrentFrame();
  const T = useTheme();
  const {width, height} = useVideoConfig();
  return (
    <AbsoluteFill aria-hidden style={{pointerEvents: 'none'}}>
      {items.map((s, i) => {
        const period = 270 + i * 30; // 9-11 s per float cycle
        const ph = (s.phase ?? i * 1.7) + (f / period) * Math.PI * 2;
        const dx = Math.cos(ph) * 3;
        const dy = Math.sin(ph) * 7;
        const scale = kf(f, [at + i * 3, at + i * 3 + 16], [0.6, 1], pop);
        const o = kf(f, [at + i * 3, at + i * 3 + 8], [0, 1]);
        const color = T[s.hue];
        return (
          <svg
            key={i}
            viewBox="0 0 100 100"
            width={s.size}
            height={s.size}
            style={{
              position: 'absolute',
              left: s.x * width - s.size / 2 + dx,
              top: s.y * height - s.size / 2 + dy,
              opacity: o * T.shapes.opacity,
              transform: `scale(${scale})`,
              overflow: 'visible',
              filter: T.shapes.glow ? `drop-shadow(0 0 ${T.shapes.glow}px ${color})` : undefined,
            }}
          >
            <Shape form={s.form} color={color} spin={f * 0.12} />
          </svg>
        );
      })}
    </AbsoluteFill>
  );
};

// Placements per scene: corners and edges, behind the content.
export const SHAPES: Record<'pain' | 'name' | 'learn' | 'demo' | 'setup' | 'end', ShapeSpec[]> = {
  pain: [
    {form: 'sun', x: 0.97, y: 0.04, size: 230, hue: 'pink'},
    {form: 'tile', x: 0.03, y: 0.95, size: 160, hue: 'yellow'},
    {form: 'orbit', x: 0.99, y: 0.9, size: 200, hue: 'green'},
  ],
  name: [
    {form: 'sun', x: 0.1, y: 0.14, size: 190, hue: 'yellow'},
    {form: 'dawn', x: 0.92, y: 0.12, size: 170, hue: 'green'},
    {form: 'peak', x: 0.9, y: 0.86, size: 180, hue: 'pink'},
    {form: 'orbit', x: 0.08, y: 0.86, size: 210, hue: 'orange'},
  ],
  learn: [
    {form: 'tile', x: 0.06, y: 0.1, size: 150, hue: 'pink'},
    {form: 'orbit', x: 0.94, y: 0.12, size: 200, hue: 'yellow'},
    {form: 'dawn', x: 0.95, y: 0.95, size: 180, hue: 'orange'},
  ],
  demo: [
    {form: 'sun', x: 0.98, y: 0.02, size: 220, hue: 'green'},
    {form: 'dawn', x: 0.02, y: 0.98, size: 180, hue: 'pink'},
    {form: 'tile', x: 0.99, y: 0.97, size: 130, hue: 'orange'},
  ],
  setup: [
    {form: 'voice', x: 0.9, y: 0.07, size: 200, hue: 'orange'},
    {form: 'sun', x: 0.04, y: 0.07, size: 170, hue: 'pink'},
    {form: 'peak', x: 0.96, y: 0.96, size: 170, hue: 'green'},
    {form: 'tile', x: 0.03, y: 0.94, size: 130, hue: 'yellow'},
  ],
  end: [
    {form: 'sun', x: 0.92, y: 0.12, size: 220, hue: 'yellow'},
    {form: 'orbit', x: 0.08, y: 0.16, size: 200, hue: 'pink'},
    {form: 'dawn', x: 0.07, y: 0.9, size: 190, hue: 'green'},
    {form: 'peak', x: 0.93, y: 0.9, size: 150, hue: 'orange'},
  ],
};
