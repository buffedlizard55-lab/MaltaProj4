// A pinned clock for the browser suites, so a layout or copy assertion cannot
// start failing merely because the committed snapshot has aged.
//
// Why this exists (found 2026-10-24). The generated pages compare the snapshot
// they were built from with the *reader's* clock: `expire()` in assets/app.js
// hides current picks and blanks the counters once `Date.now() - observed` is
// past the eight-hour evidence window, and shows the stale banner instead. Three
// suites asserted "the board shows picks" or "a fresh snapshot has no stale
// banner" while running on the wall clock, so they were true only for eight
// hours after a build and then failed -- or crashed on a null row -- for every
// later run. On 2026-10-24 the published snapshot was 17h47m old, because the
// refresh pipeline had been failing since the previous afternoon, and those
// suites were red for a reason that had nothing to do with what they test.
//
// The product behaviour is correct and unchanged: a stale snapshot really must
// stop advertising current picks. What the tests need is to say *which* moment
// they are measuring. `pinClock` answers that, and it must pin the `Date`
// constructor as well as `Date.now()`, because the suites build timestamps with
// `new Date(...)` as well as reading the clock.
//
// Usage:
//   const {clockScript} = require('./pinned-clock.cjs');
//   await page.addInitScript({content: clockScript(epochMs)});
//   // or, for a page that is already open:
//   await page.evaluate(clockScript(epochMs));

/** Source of an init script that freezes the page clock at `epochMs`. */
function clockScript(epochMs) {
  const pinned = Math.trunc(epochMs);
  return `(() => {
    const RealDate = Date;
    const PINNED = ${pinned};
    class PinnedDate extends RealDate {
      constructor(...args) {
        if (args.length === 0) super(PINNED);
        else super(...args);
      }
      static now() { return PINNED; }
    }
    PinnedDate.parse = RealDate.parse;
    PinnedDate.UTC = RealDate.UTC;
    globalThis.Date = PinnedDate;
    window.__clockPinnedTo = PINNED;
  })();`;
}

module.exports = {clockScript};
