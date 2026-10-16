# The scheduled refresh never fired — measured, then mitigated

Session `ab18fe2a`, 2026-10-16T04:18Z (UTC).

## What was measured, and how

All figures come from the official GitHub Actions API for this repository, not from
inference:

```sh
gh api "repos/buffedlizard55-lab/MaltaProj4/actions/runs?per_page=100&page=N&event=schedule"
gh api  repos/buffedlizard55-lab/MaltaProj4/actions/workflows      # state of each workflow
```

| Measurement | Result |
|---|---|
| Total `schedule` events in the workflow's entire run history | **2** |
| 2026-10-15T16:59:51Z | success — the 12:17 slot, about **4h42m late** |
| 2026-10-15T21:22:25Z | failure — the 18:17 slot, about **3h05m late** |
| `schedule` events after the two-hour cron merged (PR #24, 23:20:34Z on 15 Oct) | **0** |
| Workflow `state` | `active` — it is scheduled and enabled |

At 04:18Z on 16 October, **4 hours 58 minutes** had passed since the two-hour cron
landed, with slots at 00:17 and 02:17 both producing nothing.

## Why it matters

The live site was serving the 00:02Z push build, whose snapshot was generated at
23:45:45Z on 15 October. Every one of its open picks carried
`expires_at = 2026-10-16T05:33:49Z`. So without a push, the *entire* pick board would
have passed its deadline at the same instant, roughly 76 minutes after this
measurement, and the site would show a full page of stale-data warnings instead of
picks.

That is the concrete failure the user's "updated every 4–8 hours" requirement is
exposed to. It is not a code defect: the build, the browser and the expiry logic all
behave correctly. It is that the trigger did not arrive.

## Two contributing constraints found

1. **GitHub delays, and may drop, scheduled jobs.** Both observed runs were 3–5 hours
   late. With a six-hour or even two-hour cron, one missed slot is a multi-hour gap.
2. **This project's GitHub App token cannot dispatch workflows.** `gh workflow run
   pages.yml --ref main` returned
   `HTTP 403: Resource not accessible by integration` against
   `/actions/workflows/383957342/dispatches`. So a manual or agent-driven trigger is not
   available; a push to `main` is the only trigger this project can reliably drive
   itself.

## Mitigation applied

`.github/workflows/pages.yml`: `cron: '17 */2 * * *'` → **`cron: '17 * * * *'`**
(twelve slots a day instead of six), with the measurement recorded in a comment beside
it.

Rationale: GitHub's delay is roughly independent of the requested cadence. Twelve
attempts a day make it far likelier that at least one lands inside the eight-hour
evidence window than six do, and a delayed hourly run is still a fresh refresh. Each
run is idempotent — it refreshes, audits row by row, builds, validates, and deploys the
verified artifact — so a redundant run changes nothing except the timestamps.

This also keeps the promise in the footer text honest, which now reads "hourly at :17
UTC" in the methodology page.

## What this does *not* claim

- It is a risk reduction, **not** a fix. GitHub states scheduled events may be delayed
  or dropped under load; no cron can guarantee delivery, and this session does not
  claim the 4–8 hour window is now guaranteed.
- It does not change the safety behaviour. Expiry is enforced at build time and again
  in the browser, so the failure mode remains a visible staleness warning rather than a
  wrong number. The last successful snapshot is retained on failure and never
  relabelled fresh.
- Extra runs consume Actions minutes. The repository is public, where Actions is free,
  and the workflow is capped at 15 minutes with `cancel-in-progress: false`.

## Verification performed

- `gh api .../actions/workflows` → all workflows `active` (so this was never a disabled schedule).
- `gh api .../actions/runs?event=schedule` across all 135 runs → exactly the two events above.
- `gh workflow run` → the 403 above, recorded rather than worked around. No credentials
  were requested and no permission was escalated.
- Published as flagged irregularity `scheduled-refresh-gap-2026-10-16` on Flagged for Review.
