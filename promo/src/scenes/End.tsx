import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {COPY, END} from '../constants';
import {FONT, enter, popScale} from '../theme';
import {useTheme} from '../themes';
import {Pill, PopHeadline} from '../components/Text';
import {Cursor} from '../components/Cursor';
import {SHAPES, Shapes} from '../components/Shapes';

// 23.5-26 s: free & open source, the install line, the link, and the galaxy cursor with its green star.
export const End: React.FC = () => {
  const f = useCurrentFrame();
  const T = useTheme();
  const {width} = useVideoConfig();
  const wide = width > 1080;
  const pill = enter(f, END.pill, 14);
  const url = enter(f, END.url, 16);
  const cs = popScale(f, 0, 16);
  const cursorScale = wide ? 2.6 : 1.9;
  const box = 128 * cursorScale;

  return (
    <AbsoluteFill>
      <Shapes items={SHAPES.end} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', flexDirection: wide ? 'row' : 'column', gap: wide ? 60 : 22}}>
        <div style={{position: 'relative', width: box, height: box, transform: `scale(${cs})`, flex: 'none'}}>
          {/* tip at (4, 4) of the art, so this fills the box */}
          <Cursor x={4 * cursorScale} y={4 * cursorScale} look="copied" scale={cursorScale} />
        </div>
        <div style={{display: 'flex', flexDirection: 'column', alignItems: wide ? 'flex-start' : 'center'}}>
          <PopHeadline text={COPY.endTitle} at={END.title} size={wide ? 96 : 76} style={{textAlign: wide ? 'left' : 'center'}} />
          <div style={{marginTop: 30, opacity: pill, transform: `scale(${0.9 + 0.1 * pill})`}}>
            <Pill text={COPY.endPill} size={44} />
          </div>
          <div
            style={{
              marginTop: 26,
              fontFamily: FONT.body,
              fontWeight: 700,
              fontSize: 46,
              opacity: url,
              transform: `translateY(${(1 - url) * 18}px)`,
              textAlign: wide ? 'left' : 'center',
            }}
          >
            <span style={{color: T.ink3}}>{COPY.urlHost}</span>
            {!wide && <br />}
            <span style={{color: T.ink}}>{COPY.urlPath}</span>
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
