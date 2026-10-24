# Session e9be3e6b verification

Two independent checks, both zero-network against the committed snapshot.

```bash
# 1. Replay every row from its own stored evidence; prove eight corruptions are caught.
python3 verification-e9be3e6b/verify_source_ladder.py \
  --snapshot data/latest.json --self-test \
  --output research/session-e9be3e6b/source-ladder-audit.json

# 2. Measure the built artifact on real phone viewports (requires npm ci first).
python3 -m scripts.build --data data/latest.json
node verification-e9be3e6b/mobile_probe.cjs
```

The first command exits 1 on any failure; the second writes
`research/session-e9be3e6b/mobile-measurements.json` and asserts the executive-summary bar
is above the pick list, the first pick and both percentages are above the fixed tab bar at
320x568, no page overflows, every open row has an official Hotspawn link plus an external
price link, and the separate unresolved/limitations section is present.

Neither script imports `scripts.refresh` or any collector module. Reading official pages was
done separately with the agent's `fetch_page`/`web_search` tools and recorded in
`research/session-e9be3e6b/SOURCE-OBSERVATIONS.json`; the sandbox's own `curl` is TLS-blocked
for those hosts, so a network-dependent verifier would give a false "source down" result here.
