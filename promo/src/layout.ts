// Rectangles for each size. One composition, two layouts: square and wide.

export type Rect = {x: number; y: number; w: number; h: number};

export const M = 80; // safe margin
export const TERM = {titleH: 56, pad: 28, gutter: 76, lineH: 42, font: 25, charW: 12.6};

export const layout = (width: number, height: number) => {
  const wide = width > height;
  return {
    wide,
    painTerm: wide
      ? {x: 360, y: M, w: 1200, h: 700}
      : {x: M, y: M, w: width - 2 * M, h: 700},
    term: wide
      ? {x: M, y: M, w: 1100, h: 700}
      : {x: M, y: M, w: width - 2 * M, h: 480},
    input: wide
      ? {x: 1240, y: 330, w: width - 1240 - M, h: 200}
      : {x: M, y: 588, w: width - 2 * M, h: 170},
    // vertical centre of the caption line at the bottom
    captionY: 958,
    // top-left of the small gesture card in the demo, above the caption
    // wide: clear of the log window even at the 1.06x camera push (its bottom reaches ~818);
    // square: between the input box and the caption
    corner: {x: M, y: wide ? 836 : 774},
    painCaptionY: 900,
  };
};

/** Centre of a visible terminal row. */
export const rowY = (t: Rect, row: number) =>
  t.y + TERM.titleH + TERM.pad + row * TERM.lineH + TERM.lineH / 2;

/** Left edge of the log text. */
export const textX = (t: Rect) => t.x + TERM.pad + TERM.gutter;

export const visibleRows = (t: Rect) =>
  Math.floor((t.h - TERM.titleH - 2 * TERM.pad) / TERM.lineH);
