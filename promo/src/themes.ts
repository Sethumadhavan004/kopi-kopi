import {createContext, useContext} from 'react';

// Every colour in the video. Scenes read from the active theme, never hard-code.
// Hikari = light, Ankoku = dark, both from the HIKARI design system.

export type Theme = {
  name: 'hikari' | 'ankoku';
  dark: boolean;
  paper: string; // background
  surface: string; // windows, cards, input box
  line: string; // 2px borders, dividers
  ink: string; // headlines, primary text
  ink2: string; // body text, log text
  ink3: string; // line numbers, small labels
  red: string; // ONE red moment per screen at most
  redText: string; // ERROR level in logs
  pink: string;
  pinkTint: string;
  yellow: string;
  yellowTint: string;
  green: string;
  greenTint: string;
  greenText: string;
  orange: string; // decorative shapes only
  onPastel: string; // any text on pink/yellow/green
  shadowLift: string; // cards on lift only
  shadowWindow: string;
  dragSelect: {color: string; alpha: number}; // the ordinary trackpad selection
  warnAsChip: boolean; // pastel yellow text is unreadable on white, so Hikari uses a chip
  cursor: {fill: string; stroke: string; glow: string}; // plain arrow + glow behind the galaxy
  pad: {fill: string; shadow: string}; // fingertip pads on the gesture card's trackpad
  shapes: {opacity: number; glow: number}; // floating forms: solid in Hikari, soft glow in Ankoku
  wipeTint: boolean; // Sun-disc transitions use the tint, not the pastel, in the dark
  stars: boolean;
};

// The hue tokens are shared by both themes.
const HUES = {
  red: '#D2371F',
  pink: '#F6B9C4',
  yellow: '#F9E79F',
  green: '#BFE6CB',
  orange: '#F39A5B',
};

export const THEMES = {
  hikari: {
    name: 'hikari',
    dark: false,
    ...HUES,
    paper: '#FFF4F0',
    surface: '#FFFFFF',
    line: '#F3D3D8',
    ink: '#2B1215',
    ink2: '#5A3A3E',
    ink3: '#6B4A4E',
    redText: '#B8301F',
    pinkTint: '#FCE4E8',
    yellowTint: '#FDF3C8',
    greenTint: '#E3F4E8',
    greenText: '#2F5A3C',
    onPastel: '#2B1215',
    shadowLift: '0 22px 44px -20px rgba(184,48,31,0.45)',
    shadowWindow: '0 24px 48px -30px rgba(43,18,21,0.35)',
    dragSelect: {color: '#CFE0FF', alpha: 1},
    warnAsChip: true,
    cursor: {fill: '#FFFFFF', stroke: '#120A0B', glow: '#AA5AFF22'},
    pad: {fill: '#2B121524', shadow: '0 8px 12px -4px #2B12151F'}, // ink at ~14%
    shapes: {opacity: 0.95, glow: 0},
    wipeTint: false,
    stars: false,
  },
  ankoku: {
    name: 'ankoku',
    dark: true,
    ...HUES,
    paper: '#120A0B',
    surface: '#1E1315',
    line: '#3A2428',
    ink: '#FFF1EC',
    ink2: '#D8BCC0',
    ink3: '#B89CA0',
    redText: '#FF8A73',
    pinkTint: '#3A1D24',
    yellowTint: '#362E15',
    greenTint: '#17301F',
    greenText: '#8FD6A6',
    onPastel: '#2B1215',
    shadowLift: '0 22px 44px -20px rgba(184,48,31,0.45)',
    shadowWindow: '0 30px 80px #00000066',
    dragSelect: {color: '#466EFF', alpha: 0.35},
    warnAsChip: false,
    cursor: {fill: '#FFF1EC', stroke: '#120A0B', glow: '#AA5AFF38'},
    pad: {fill: '#FFF1EC38', shadow: '0 8px 14px -4px #00000080'}, // ink at ~22%
    shapes: {opacity: 0.2, glow: 28},
    wipeTint: true,
    stars: true,
  },
} satisfies Record<string, Theme>;

export type ThemeName = keyof typeof THEMES;
export type Hue = 'pink' | 'yellow' | 'green' | 'orange';

/** A pastel hue's quiet tint, where one exists. */
export const tintOf = (t: Theme, hue: Hue) =>
  hue === 'pink' ? t.pinkTint : hue === 'yellow' ? t.yellowTint : hue === 'green' ? t.greenTint : t.orange;

// The composition passes its `theme` prop into this context once (in Video.tsx),
// so any component can read colours without threading props through every layer.
export const ThemeCtx = createContext<Theme>(THEMES.ankoku);
export const useTheme = () => useContext(ThemeCtx);
