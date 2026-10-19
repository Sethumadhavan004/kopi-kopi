import {Composition, Sequence} from 'remotion';
import {FPS, GIF, TOTAL_FRAMES} from './constants';
import {Video, VideoProps} from './Video';

// The README GIF: the same video, shifted so the demo starts at frame 0.
const DemoWindow: React.FC<VideoProps> = (props) => (
  <Sequence from={-GIF.from}>
    <Video {...props} />
  </Sequence>
);

const SIZES = [
  {id: 'Square', width: 1080, height: 1080},
  {id: 'Wide', width: 1920, height: 1080},
] as const;
const THEME_IDS = [
  {id: 'Hikari', theme: 'hikari'},
  {id: 'Ankoku', theme: 'ankoku'},
] as const;

// Four compositions from one component: the theme is just a prop.
export const Root: React.FC = () => (
  <>
    {SIZES.flatMap((s) =>
      THEME_IDS.map((t) => (
        <Composition
          key={`${s.id}-${t.id}`}
          id={`${s.id}-${t.id}`}
          component={Video}
          width={s.width}
          height={s.height}
          fps={FPS}
          durationInFrames={TOTAL_FRAMES}
          defaultProps={{theme: t.theme} as VideoProps}
        />
      )),
    )}
    {THEME_IDS.map((t) => (
      <Composition
        key={`DemoGif-${t.id}`}
        id={`DemoGif-${t.id}`}
        component={DemoWindow}
        width={1080}
        height={1080}
        fps={FPS}
        durationInFrames={GIF.frames}
        defaultProps={{theme: t.theme} as VideoProps}
      />
    ))}
  </>
);
