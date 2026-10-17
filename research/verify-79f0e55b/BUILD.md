# Where this directory's evidence came from

Everything in this directory is generated from captured raw bytes, not typed by hand.

| File | Produced by | Raw evidence it reads |
| --- | --- | --- |
| `VERIFICATION.md`, `twc-2026-verified.json` | `python -m scripts.verify_report_79f0e55b` | `research/hltv-79f0e55b/report.json`, `research/harvest-79f0e55b/{snapshot.json,probe-report.json,logs/refresh.txt}`, `research/live-79f0e55b/report.json`, `research/verify-79f0e55b/vrs/*.md` |
| `vrs/americas.md`, `vrs/asia.md`, `vrs/europe.md` | Valve's own published regional standings, fetched byte-for-byte through the GitHub contents API and base64-decoded unchanged | `https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/contents/live/2026/standings_{americas,asia,europe}_2026_10_05.md` (repo commit `eec4853d7bcf0f1f7efe7f0d901234bef7e98b75`) |

Hashes are recorded in `VERIFICATION.md`; re-running the generator reproduces the same tables from the same bytes, and
`python -m scripts.hltv_verify_79f0e55b --replay research/hltv-79f0e55b` re-parses the HLTV bodies offline, which is how
the parser fixes in this session were checked before the next network run.
