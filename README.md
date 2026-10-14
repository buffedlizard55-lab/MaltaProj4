# Hotspawn CS2 Scout

An independent, mobile-first research dashboard for **every CS2 fixture returned by Hotspawn’s public lobby feed**. Hotspawn supplies match membership and lock times, **never win probabilities**.

## The site

**[Executive summary](https://buffedlizard55-lab.github.io/MaltaProj4/)** · **[Updated picks](https://buffedlizard55-lab.github.io/MaltaProj4/picks.html)** · [All matches](https://buffedlizard55-lab.github.io/MaltaProj4/matches.html) · [Unresolved picks](https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html) · [Flagged for Review](https://buffedlizard55-lab.github.io/MaltaProj4/review.html) · [Sources & methodology](https://buffedlizard55-lab.github.io/MaltaProj4/sources.html)

The dashboard is not affiliated with Hotspawn or any betting operator. It does not place bets, submit picks, or require a login/API key.

## How it works

1. Read the official [CS2 lobby](https://play.hotspawn.com/cs2-pickems) and its Angular hydration data. Compare it with the exact [tenant-1 scheduled-CS2 fixture query](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1), observed in Hotspawn’s own public JavaScript.
2. Keep **all** returned CS2 entries, not just high-tier or externally covered matches. Separate open picks from past-lock/end-time records; do not reinterpret stale `scheduled` status as an upcoming match.
3. Discover CS2 in [Polymarket’s official registry](https://gamma-api.polymarket.com/sports) and paginate active events. Require whole-match moneyline, two teams, exact UTC start, open market, fresh update, two-sided price, usable liquidity/spread. Only case/punctuation and source-published abbreviations are normalized, plus the small [primary-source-verified alias register](data/identities.json).
4. **Only unresolved matches** enter fallback research: HLTV match discovery and individual match context, then Pinnacle’s official public esports moneylines, then Thunderpick/GG.BET access checks. The latter two have no verified automated line adapter at launch; access/JavaScript/security limitations are explicitly logged. No access controls are bypassed.
5. Produce our own **calculated fair lines**: normalize exchange outcome prices, or convert and de-vig a complete bookmaker pair; fair decimal odds = `1 / probability`. These are derived market estimates, not verified true chances or a new calibrated statistical model. Fallbacks never overwrite accepted primary picks.
6. If a price or identity cannot be established, **leave it blank** and publish the attempts, candidate identity conflicts and limitations. Never manufacture 50/50, use fan votes, convert rank to probability, or conflate academy/main squads.

Full research notes: [research/FINDINGS.md](research/FINDINGS.md). Every displayed row links to Hotspawn and an [evidence ledger](https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html). The raw accepted price inputs, primary fixture fields, source URLs, observed timestamps and response hashes are downloadable as JSON; the match table also exports CSV.

## Automatic operation

`.github/workflows/pages.yml` checks and publishes on changes to main, on manual workflow dispatch, and at **00:17, 06:17, 12:17, 18:17 UTC** (six-hour cadence). No routine user input is needed. GitHub schedules can be delayed; public-repository scheduled workflows can be disabled by GitHub after extended inactivity. This is a target, not a delivery guarantee.

- Scheduled runs restore the latest snapshot from Actions cache (committed `data/latest.json` is a bootstrap fallback), refresh sources, test, build, and deploy a Pages artifact. They do **not** push generated data to main or create branches.
- Cache preserves the last good fixture list if discovery fails or a populated list unexpectedly becomes empty. Freshness timestamps are not renewed on failure.
- Source timestamps and cache age are retained. Prices older than eight hours or past a Hotspawn pick lock are withheld at build time and in the browser. Source failures do not mean there are no matches.
- A failed build/verification prevents deployment. The previous site remains live with client-side stale warnings. Actions stores source-response archives, data and test reports for seven days. Durable row-level evidence is in the published JSON.
- [Workflow history](https://github.com/buffedlizard55-lab/MaltaProj4/actions) is public. The Sources and Review pages distinguish successful HTTP access from an accepted quote.

## Run locally

Python 3.11+ builds the static site. Node 22 is needed only for browser verification.

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m scripts.build
python -m scripts.validate
python -m http.server 8000 --bind 0.0.0.0 --directory public
```

Refresh from public sources (outbound network access required):

```sh
python -m scripts.refresh --output runtime/latest.json
python -m scripts.build --data runtime/latest.json
python -m scripts.validate --data runtime/latest.json
```

Browser/accessibility verification (a self-contained local test server is started and closed by the test):

```sh
npm ci --ignore-scripts
npm run test:browser
```

Tests cover probability arithmetic, wrong-game/map/handicap exclusions, exact/reversed/ambiguous identity, source-supplied abbreviations, malformed and stale lines, lock times, fan-percentage independence, failed/empty/schema-changed source retention, every internal link, every sourced row, subpath deployment, mobile/tablet/desktop overflow, WCAG A/AA scans, navigation, filters and expiry. Test fixtures are labeled official HTML excerpts; test-only hypothetical teams never enter published match data.

## Layout

- `scripts/core.py`: fixture normalization, strict identity matching and price calculations.
- `scripts/hltv.py`: missing-match discovery and attributable HLTV context; no fan-vote model.
- `scripts/refresh.py`: source requests, receipt/archive collection, refresh orchestration and last-good retention.
- `scripts/build.py`, `site/assets/`: pre-rendered dashboard, responsive UI and progressive enhancement.
- `scripts/validate.py`, `tests/`: row audit, links, unit/failure tests and browser/accessibility checks.
- `data/latest.json`: initial verified snapshot, **not a permanently current dataset**. Production JSON updates on Pages independently of Git.
- `COORDINATION.md`: shared ownership, verification record and deployment log.

Missing data and flagged irregularities are intentional, visible outputs—not placeholders to be filled with guesses. Market prices are uncertain and can be illiquid or wrong. This project does not establish profitable betting value or guarantee outcomes.
