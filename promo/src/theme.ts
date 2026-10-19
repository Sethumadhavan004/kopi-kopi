import {Easing, interpolate} from 'remotion';
import {loadFont as loadMochiy} from '@remotion/google-fonts/MochiyPopOne';
import {loadFont as loadZenMaru} from '@remotion/google-fonts/ZenMaruGothic';
import {loadFont as loadMono} from '@remotion/google-fonts/MPLUS1Code';
import type {Theme} from './themes';

// Fonts, motion curves and keyframe helpers. Colours live in themes.ts.

export const FONT = {
  head: loadMochiy('normal', {weights: ['400'], subsets: ['latin']}).fontFamily,
  body: loadZenMaru('normal', {weights: ['500', '700'], subsets: ['latin']}).fontFamily,
  mono: loadMono('normal', {weights: ['400', '500'], subsets: ['latin']}).fontFamily,
};

// The only two curves in the video (plus expo for the one count-up the brief asks for).
export const soft = Easing.bezier(0.16, 1, 0.3, 1); // soft landings
export const pop = Easing.bezier(0.34, 1.56, 0.64, 1); // small overshoot pops
export const expoOut = Easing.out(Easing.exp);

/** Keyframes: value at each frame, eased between them, held before and after. */
export const kf = (frame: number, frames: number[], values: number[], easing = soft) =>
  interpolate(frame, frames, values, {
    easing,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

/** 0 -> 1 over `dur` frames starting at `start`. */
export const enter = (frame: number, start: number, dur = 14, easing = soft) =>
  kf(frame, [start, start + dur], [0, 1], easing);

/** The headline letter pop: scale 0 -> 1.18 -> 1. */
export const popScale = (frame: number, start: number, dur = 12) =>
  kf(frame, [start, start + dur * 0.6, start + dur], [0, 1.18, 1]);

export type Look = 'plain' | 'armed' | 'selecting' | 'copied';

/** The star colour for each cursor look; the last caption (paste) uses ink. */
export const starColor = (t: Theme, look: Look) =>
  look === 'armed' ? t.yellow : look === 'selecting' ? t.pink : look === 'copied' ? t.green : t.ink;
