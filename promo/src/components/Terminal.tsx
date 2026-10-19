import {FONT} from '../theme';
import {useTheme} from '../themes';
import {Rect, TERM, visibleRows} from '../layout';
import {LOG} from '../logs';

export type Selection = {from: number; to: number; color: string; alpha: number; text?: string};

/**
 * A mock terminal. `scroll` is the log line shown on the top row (can be fractional).
 * Selections are in log-line indices, so they scroll with the text.
 */
export const Terminal: React.FC<{
  rect: Rect;
  scroll: number;
  title: string;
  selection?: Selection;
  caret?: {line: number; color: string; alpha: number};
  rangeMark?: {from: number; to: number; color: string; alpha: number};
  opacity?: number;
  dy?: number;
}> = ({rect, scroll, title, selection, caret, rangeMark, opacity = 1, dy = 0}) => {
  const T = useTheme();
  const rows = visibleRows(rect);
  const first = Math.floor(scroll);
  const bodyTop = TERM.titleH + TERM.pad;
  const bodyH = rect.h - TERM.titleH - 2 * TERM.pad;
  const yOf = (line: number) => (line - scroll) * TERM.lineH;
  const levelColor = (level: string) =>
    level === 'ERROR' ? T.redText : level === 'WARN' ? T.yellow : T.ink3;

  // scrollbar
  const trackH = rect.h - TERM.titleH - 24;
  const total = LOG.length;
  const thumbH = Math.max(28, (rows / total) * trackH);
  const thumbY = (scroll / (total - rows)) * (trackH - thumbH);

  const inSelection = (i: number) =>
    selection?.text && selection.alpha > 0.5 && i >= selection.from && i <= selection.to;

  return (
    <div
      style={{
        position: 'absolute',
        left: rect.x,
        top: rect.y + dy,
        width: rect.w,
        height: rect.h,
        background: T.surface,
        border: `2px solid ${T.line}`,
        borderRadius: 24,
        overflow: 'hidden',
        opacity,
        boxShadow: T.shadowWindow,
      }}
    >
      {/* title bar */}
      <div
        style={{
          height: TERM.titleH,
          borderBottom: `2px solid ${T.line}`,
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          paddingLeft: 24,
        }}
      >
        {[0, 1, 2].map((i) => (
          <div key={i} style={{width: 14, height: 14, borderRadius: 7, background: T.line}} />
        ))}
        <div
          style={{
            marginLeft: 14,
            fontFamily: FONT.mono,
            fontSize: 20,
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            color: T.ink3,
          }}
        >
          {title}
        </div>
      </div>

      {/* log body */}
      <div
        style={{
          position: 'absolute',
          left: TERM.pad,
          right: TERM.pad + 18,
          top: bodyTop,
          height: bodyH,
          overflow: 'hidden',
          fontFamily: FONT.mono,
          fontSize: TERM.font,
          whiteSpace: 'pre',
        }}
      >
        {selection && selection.alpha > 0 && (
          <div
            style={{
              position: 'absolute',
              left: TERM.gutter - 8,
              right: 0,
              top: Math.max(-10, yOf(selection.from)),
              height: Math.max(0, yOf(selection.to + 1) - Math.max(-10, yOf(selection.from))),
              background: selection.color,
              opacity: selection.alpha,
              borderRadius: 8,
            }}
          />
        )}
        {Array.from({length: rows + 2}, (_, k) => {
          const i = first + k;
          const l = LOG[i];
          if (!l) return null;
          const sel = inSelection(i);
          const warnChip = l.level === 'WARN' && T.warnAsChip;
          return (
            <div
              key={l.n}
              style={{
                position: 'absolute',
                top: yOf(i),
                height: TERM.lineH,
                lineHeight: `${TERM.lineH}px`,
                left: 0,
              }}
            >
              <span style={{color: T.ink3, opacity: 0.7, display: 'inline-block', width: TERM.gutter}}>
                {String(l.n).padStart(4, ' ')}
              </span>
              <span style={{color: sel ? selection!.text : T.ink3}}>{l.time}  </span>
              {warnChip ? (
                <span>
                  <span style={{background: T.yellow, color: T.onPastel, borderRadius: 6, padding: '2px 4px', margin: '0 -4px'}}>WARN</span>
                  {'   '}
                </span>
              ) : (
                <span style={{color: levelColor(l.level)}}>{l.level.padEnd(5)}  </span>
              )}
              <span style={{color: sel ? selection!.text : T.ink2}}>{l.msg}</span>
            </div>
          );
        })}
        {caret && caret.alpha > 0 && (
          <div
            style={{
              position: 'absolute',
              left: TERM.gutter - 6,
              top: yOf(caret.line) + 4,
              width: 5,
              height: TERM.lineH - 8,
              borderRadius: 3,
              background: caret.color,
              opacity: caret.alpha,
              boxShadow: `0 0 14px ${caret.color}`,
            }}
          />
        )}
      </div>

      {/* scrollbar, with the selected range marked on it */}
      <div style={{position: 'absolute', right: 10, top: TERM.titleH + 12, width: 8, height: trackH, borderRadius: 4, background: T.line}}>
        <div style={{position: 'absolute', top: thumbY, width: 8, height: thumbH, borderRadius: 4, background: T.ink3, opacity: 0.5}} />
        {rangeMark && rangeMark.alpha > 0 && (
          <div
            style={{
              position: 'absolute',
              left: -3,
              width: 14,
              top: (rangeMark.from / total) * trackH,
              height: Math.max(6, ((rangeMark.to - rangeMark.from + 1) / total) * trackH),
              borderRadius: 7,
              background: rangeMark.color,
              opacity: rangeMark.alpha,
              boxShadow: `0 0 0 2px ${T.surface}`,
            }}
          />
        )}
      </div>
    </div>
  );
};
