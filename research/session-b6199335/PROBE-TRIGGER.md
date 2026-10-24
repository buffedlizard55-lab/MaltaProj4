# Probe trigger (session b6199335)

This file exists only to trigger `.github/workflows/probe-b6199335.yml`, which
runs a one-off, read-only source capture on the GitHub runner because this
session's sandbox can reach GitHub only. It writes raw responses under
`research/session-b6199335/raw/` and uploads them as an artifact. Nothing in the
pipeline reads this directory.
<!-- re-trigger 3 -->
