// Every word and every timing in the video lives here.
// Timings are in frames: 30 frames = 1 second.

export const FPS = 30;

// Where each scene starts on the main timeline, and how long it lasts.
export const SCENES = {
  pain: {from: 0, dur: 120}, // 0-4 s
  name: {from: 120, dur: 90}, // 4-7 s
  learn: {from: 210, dur: 75}, // 7-9.5 s: learn the gesture
  demo: {from: 285, dur: 360}, // 9.5-21.5 s
  setup: {from: 645, dur: 135}, // 21.5-26 s
  end: {from: 780, dur: 75}, // 26-28.5 s
};
export const TOTAL_FRAMES = SCENES.end.from + SCENES.end.dur;

export const COPY = {
  pain: 'copying long logs on a trackpad?',
  name: 'kopi-kopi.',
  tagline: 'copy & paste with taps.',
  learn: 'three-finger tap · or wheel click',
  gestureOr: 'or',
  terminalTitle: 'build.log',
  inputLabel: 'claude code',
  steps: [
    'three-finger tap', // the learn beat already taught "or wheel click"
    'tap the start',
    'tap the end · copied',
    'three-finger tap · pasted',
  ],
  setupTitle: 'setup.',
  // "→" is drawn as a small arrow shape, so it matches the font everywhere
  setup: [
    {main: 'touchpad: three-finger tap → middle click', sub: 'mouse: nothing to set up'},
    {pill: 'pip install kopi-kopi', sub: 'or download the Windows app'},
    {main: 'tap.'},
  ],
  endTitle: 'free & open source.',
  endPill: 'pip install kopi-kopi',
  urlHost: 'github.com/',
  urlPath: 'Sethumadhavan004/kopi-kopi',
};

// The pain scene, in frames from its start.
export const PAIN = {
  caption: 6,
  press: 14, // finger goes down on the first line
  reachEdge: 40, // dragged to the bottom edge: auto-scroll starts
  slip: 84, // finger slips: the selection is lost
  scrollLines: 50, // how far auto-scroll runs before the slip
};

export const NAME = {title: 6, tagline: 28, infinity: [0, 84]}; // infinity draws in 2.8 s

// The learn beat: the gesture card, large and centred, presses once.
export const LEARN = {cardIn: 0, caption: 8, press: 18};

// The gesture card's own timing, in frames after the press starts.
export const GESTURE = {
  down: 5, // pads land (spring curve)
  up: 14, // pads lift back (soft curve)
  wheelDelay: 12, // the mouse wheel lights 0.4 s after the pads
  cornerWheelDelay: 4, // in the demo's small card the wheel lights almost together
  cornerScale: 0.45,
  slideIn: 9, // 0.3 s
  outAfter: 18, // slides out 0.6 s after the step lands
};

// The demo scene, in frames from its start. One continuous shot.
// Each caption stays at least 2 s (60 frames) after its action lands.
export const DEMO = {
  trigger1: 20, // three-finger tap (or wheel click): kopi mode on
  armed: 24,
  moveToStart: [60, 84],
  tapStart: 88,
  scroll: [140, 180], // the log scrolls a long way
  moveToEnd: [150, 182],
  tapEnd: 186,
  copied: 190,
  moveToInput: [248, 276],
  trigger2: 282, // three-finger tap at the input box: paste
  pasted: 288,
  countUp: 24, // frames for the "+205 lines" chip to count up (it appears at the first non-zero value)
  startRow: 2, // visible row of the start tap
  endRow: 7, // visible row of the end tap, after scrolling
  scrollLines: 200,
  // camera push toward the cursor on each tap
  push: {scale: 1.06, in: 18, hold: 22, out: 26},
};

// Setup cards pop in 100 ms (3 frames) apart, after the title, then settle flat.
export const SETUP = {title: 4, firstCard: 14, gap: 3, settle: 22};

export const END = {title: 8, pill: 24, url: 34};

// Sun-disc wipes: a disc in the next scene's accent grows from the cursor, then opens.
export const WIPE = {cover: 10, reveal: 9}; // the fully covered moment stays under ~6 frames
export const WIPES = [
  {at: SCENES.name.from, hue: 'pink', origin: 'pain-cursor'},
  {at: SCENES.setup.from, hue: 'yellow', origin: 'demo-cursor'},
  {at: SCENES.end.from, hue: 'green', origin: 'center'},
] as const;

// README GIF: the whole demo, played at 2x so it fits in 6 s.
export const GIF = {from: SCENES.demo.from, frames: SCENES.demo.dur, speed: 2, width: 600, fps: 15};
