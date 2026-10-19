import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {COPY, GESTURE, LEARN, SCENES} from '../constants';
import {enter, kf, pop} from '../theme';
import {useTheme} from '../themes';
import {layout} from '../layout';
import {CARD_H, CARD_W, GestureCard} from '../components/GestureCard';
import {Caption} from '../components/Text';
import {SHAPES, Shapes} from '../components/Shapes';

// 7-9.5 s: learn the gesture once, large and centred, before the demo uses it.
export const Learn: React.FC = () => {
  const f = useCurrentFrame();
  const T = useTheme();
  const {width, height} = useVideoConfig();
  const L = layout(width, height);
  const scale = L.wide ? 1.3 : 1.25;
  const inP = enter(f, LEARN.cardIn, 14);
  const fade = 1 - enter(f, SCENES.learn.dur - 8, 8);
  return (
    <AbsoluteFill style={{opacity: fade}}>
      <Shapes items={SHAPES.learn} />
      <div
        style={{
          position: 'absolute',
          left: width / 2 - CARD_W / 2,
          top: height * 0.44 - CARD_H / 2,
          transform: `scale(${scale * kf(f, [LEARN.cardIn, LEARN.cardIn + 12], [0.9, 1], pop)})`,
          opacity: inP,
        }}
      >
        <GestureCard t={f - LEARN.press} color={T.yellow} wheelDelay={GESTURE.wheelDelay} />
      </div>
      <Caption text={COPY.learn} at={LEARN.caption} y={L.captionY - 40} width={width} dot={T.yellow} />
    </AbsoluteFill>
  );
};
