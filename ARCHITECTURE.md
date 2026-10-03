# Architecture

## Stack and why
Offline Python ETL → static JSON → single-page vanilla JS/Canvas app. The dataset is small (89k rows, 1.7 MB of JSON), so no backend or database is needed; a static host is free, fast and cannot go down. No framework/build step keeps it easy to review and deploy.

## Data flow
`*.nakama-0` parquet (1,243 files) → `pipeline/build_data.py` → decode `event` bytes, classify bot by numeric `user_id`, normalise `ts` to seconds-from-match-start, map world→pixel → `web/data/<Map>.json` (matches → players → `p` path samples `[t,x,y]` and `e` events `[t,x,y,code]`) → browser fetches one map file on demand → filters/heatmaps computed client-side on Canvas.
Minimaps are downscaled to 1024² JPEGs (sources were 2–9k px, Lockdown 11 MB).

## Coordinate mapping
Per README: `u=(x-origin_x)/scale`, `v=(z-origin_z)/scale`, `px=u·1024`, `py=(1-v)·1024` (image Y is flipped). Only `x` and `z` are used; `y` is elevation. Done once in the ETL so the client draws in a single 1024² space. Validation: 0 of 89,104 points fall outside the image on any map, and the aggregated paths visibly follow roads/bridges/buildings on the minimap. Because mapping goes through UV, resizing the minimap preserves correctness.

## Assumptions / data issues
- **`ts` is epoch seconds, not ms** as the README says (raw values ≈1.77e9; matches then last 13 s–15 min, which is plausible; as ms they'd be <1 s). Time = `ts − min(ts)` of the match.
- **Bot = numeric `user_id`** (per README). Bot files also contain `Position`, `Loot`, `BotKill`, `BotKilled` rows, so bots are classified by id, never by event name; those are likely bot-vs-bot or bot events.
- Most matches contain one human file; bots are only recorded in a minority of matches, so counts of bots are incomplete.
- Event coordinates are the recorded player position; the victim's position for Kill events is not available.
- Minimaps are not exactly square for GrandRift (2160×2158); stretched to 1024² (<0.1% error). The dark image border is assumed out-of-bounds.
- Matches are identified by `match_id` only; the README example match files for Feb 14 are partial-day data.
- Heatmaps are not normalised across filters (each is scaled to its own 98th percentile).

## Trade-offs
| Decision | Alternative | Why |
|---|---|---|
| Static JSON, client-side heatmaps | API + DB / pre-baked heatmap PNGs | Tiny data; instant filtering; zero ops |
| Pre-map to pixels in ETL | Map in browser | One source of truth; smaller client |
| Vanilla JS + Canvas | React / Leaflet | No build; Canvas handles ~60k points fine |
| Bundled parquet reader | pyarrow only | Works offline; pyarrow is used when present |
| Short ids (8 chars) | Full UUIDs | ~40% smaller files; still unique here |
| Per-map file loaded lazily | One big file | Fast first paint |
