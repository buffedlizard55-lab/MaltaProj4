# Publication replay — session b85ad9b4

Run: https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40197667220
Captured: 2026-10-25T13:33:12.774451Z

First red step: **07-validate-fresh** (rc=1)

| # | Step | Return code |
| --- | --- | --- |
| 01 | Validate the committed board exactly as the publisher does before refreshing. | 0 |
| 02 | The unit suite the publisher runs before it refreshes. | 0 |
| 03 | Refresh every official source (Hotspawn feed and lobby, Polymarket, books, HLTV, Valve VRS). | 0 |
| 04 | Withhold any row the independent audit cannot reproduce. | 0 |
| 05 | Independent row audit of the refreshed snapshot. | 0 |
| 06 | Build the static site from the refreshed snapshot. | 0 |
| 07 | Validate the freshly built site (this is the step that fails on main). | 1 |
| 08 | Independent row audit of the built artifact. | 0 |
| 09 | The unit suite against the freshly refreshed board. | 0 |

## Snapshot counts

```json
{
  "committed": {
    "generated_at": "2026-10-25T01:47:42.430039Z",
    "rows_total": 79,
    "rows_open": 18,
    "open_with_probability": 18,
    "open_with_pick": 18,
    "open_without_pick": 0,
    "methods": {
      "bookmaker_fallback": 2,
      "exchange": 11,
      "exchange_wide": 2,
      "model_vrs": 2,
      "model_vrs_mirror": 1
    },
    "coverage": "verified"
  },
  "fresh": {
    "generated_at": "2026-10-25T13:32:27.459546Z",
    "rows_total": 78,
    "rows_open": 17,
    "open_with_probability": 17,
    "open_with_pick": 17,
    "open_without_pick": 0,
    "methods": {
      "bookmaker_fallback": 1,
      "exchange": 11,
      "exchange_wide": 1,
      "model_vrs": 4
    },
    "coverage": "verified"
  }
}
```

## Failure output: 07-validate-fresh

```
command: /opt/hostedtoolcache/Python/3.11.17/x64/bin/python -m scripts.validate --data runtime/latest.json
return code: 1
--- stdout (tail) ---

--- stderr (tail) ---
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/home/runner/work/MaltaProj4/MaltaProj4/scripts/validate.py", line 603, in <module>
    main()
  File "/home/runner/work/MaltaProj4/MaltaProj4/scripts/validate.py", line 596, in main
    report = validate_data(json.loads(Path(args.data).read_text())) | validate_site(args.site)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/MaltaProj4/MaltaProj4/scripts/validate.py", line 376, in validate_data
    validate_model_row(m, q, now)
  File "/home/runner/work/MaltaProj4/MaltaProj4/scripts/validate.py", line 122, in validate_model_row
    assert lineup_source_ok(m, team, check.get('lineup') or []), 'Model roster has no HLTV source on this row'
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Model roster has no HLTV source on this row

```
