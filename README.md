# LILA BLACK · Player Journey Explorer

Browser tool for Level Designers: replay player journeys on the minimap, see human vs bot movement, kill/death/loot/storm markers, and heatmaps (traffic, kills, deaths, loot, storm deaths).

**Live URL:** _add after deploying (see "Deploy")_ · Docs: [ARCHITECTURE.md](ARCHITECTURE.md) · [INSIGHTS.md](INSIGHTS.md)

## Tech stack
- **Pipeline:** Python 3 + Pillow (pyarrow optional; a dependency-free parquet reader is bundled in `pipeline/miniparquet.py`)
- **App:** one static `web/index.html` (vanilla JS + Canvas, no build step, no env vars)
- **Hosting:** any static host (Vercel / Netlify / GitHub Pages)

## Run locally
```bash
python pipeline/build_data.py path/to/player_data   # regenerates web/data/*.json + web/minimaps/*.jpg (already committed)
cd web && python -m http.server 8000                 # open http://localhost:8000
```

## Deploy
- **Vercel:** `vercel --prod` from the repo root (`vercel.json` serves `web/`), or import the repo in the Vercel dashboard.
- **Netlify:** set publish directory to `web`. **GitHub Pages:** serve the `web/` folder.
No environment variables are needed.

## Using the tool
1. Pick a **map**, **day**, and **match** (list shows duration and humans/bots). "All matches" aggregates.
2. Choose a **heatmap** (Traffic / Kills / Deaths / Loot / Storm deaths) and opacity.
3. With one match selected, press **Play** (1×–30×) or scrub the timeline; paths, markers and the heatmap build up over time.
4. **Time window**: two sliders (seconds since match start) restrict heatmaps, paths and markers to a phase of the match.
5. **Player filter**: isolate one player (single match: every human/bot in it; all matches: every human with their match count).
6. Toggle human paths, bot paths, event markers. Cyan = humans, orange = bots.
