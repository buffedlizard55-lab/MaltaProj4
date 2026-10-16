# Independent browser verification — ef0969b9

Run locally against the committed tree on this session's branch, using the repo's own
harness (`tests/browser.cjs`, playwright), not the site's own checks. Date: 16 October 2026.

```
npm ci --ignore-scripts
node tests/browser.cjs
```

Result (exit code 0):

> Passed: 32 page/viewport accessibility and no-overflow scans, 320/390/768/1440px layout,
> subpath URLs, navigation, filters, six legacy redirects, evidence anchors and expiry.

What this covers, and what it does not:

* **Covered:** every published route renders at 320, 390, 768 and 1440 px; no horizontal
  overflow; navigation and filters reachable; the internal links checked by the harness
  resolve; the six legacy redirect routes land on their targets; the evidence anchors
  exist; and the expiry script behaves at the exact boundary.
* **Not covered:** the live GitHub Pages bytes (the harness runs on local files), the
  scheduled-delivery behaviour of `pages.yml` (see
  `research/ef0969b9/SCHEDULER-2026-10-16.md`), and any source-data claim — browser tests
  say the page renders and links, not that a number is right.

Reproduce from the repo root; `node_modules` is not committed.
