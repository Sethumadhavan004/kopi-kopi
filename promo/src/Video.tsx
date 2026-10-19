import {AbsoluteFill, Sequence, useVideoConfig} from 'remotion';
import {PAIN, SCENES, WIPES} from './constants';
import {THEMES, ThemeCtx, ThemeName} from './themes';
import {layout} from './layout';
import {Stars} from './components/Stars';
import {Wipe} from './components/Wipe';
import {Pain, painCursor} from './scenes/Pain';
import {Name} from './scenes/Name';
import {Learn} from './scenes/Learn';
import {Demo, demoCursor} from './scenes/Demo';
import {Setup} from './scenes/Setup';
import {End} from './scenes/End';

export type VideoProps = {theme: ThemeName};

// The whole video. Inside each <Sequence>, useCurrentFrame() starts at 0.
// The `theme` prop comes from the composition (Root.tsx) and is shared through context.
export const Video: React.FC<VideoProps> = ({theme}) => {
  const T = THEMES[theme];
  const {width, height} = useVideoConfig();
  const L = layout(width, height);

  // Each wipe grows from where the cursor is when the scene ends.
  const origin = (o: (typeof WIPES)[number]['origin']) => {
    if (o === 'pain-cursor') return painCursor(PAIN.slip + 8, L.painTerm);
    if (o === 'demo-cursor') return demoCursor(SCENES.demo.dur, width, height);
    return {x: width / 2, y: height / 2};
  };

  return (
    <ThemeCtx.Provider value={T}>
      <AbsoluteFill style={{background: T.paper}}>
        <Stars />
        <Sequence from={SCENES.pain.from} durationInFrames={SCENES.pain.dur} name="1 pain">
          <Pain />
        </Sequence>
        <Sequence from={SCENES.name.from} durationInFrames={SCENES.name.dur} name="2 name">
          <Name />
        </Sequence>
        <Sequence from={SCENES.learn.from} durationInFrames={SCENES.learn.dur} name="3 learn">
          <Learn />
        </Sequence>
        <Sequence from={SCENES.demo.from} durationInFrames={SCENES.demo.dur} name="4 demo">
          <Demo />
        </Sequence>
        <Sequence from={SCENES.setup.from} durationInFrames={SCENES.setup.dur} name="5 setup">
          <Setup />
        </Sequence>
        <Sequence from={SCENES.end.from} durationInFrames={SCENES.end.dur} name="6 end">
          <End />
        </Sequence>
        {WIPES.map((w) => {
          const {x, y} = origin(w.origin);
          return <Wipe key={w.at} at={w.at} x={x} y={y} hue={w.hue} />;
        })}
      </AbsoluteFill>
    </ThemeCtx.Provider>
  );
};
