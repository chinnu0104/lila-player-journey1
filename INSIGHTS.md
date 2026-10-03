# Insights (from the tool; numbers from all 5 days, 796 matches)

## 1. Loot and fights are concentrated in a few hotspots
- **Seen:** On Ambrose Valley the top 10% of 32×32 map cells hold 63% of all movement, **88% of bot kills and 90% of loot**; loot appears in only 25% of cells (Grand Rift 12%, Lockdown 15%). Use *Loot* and *Kills* heatmaps.
- **Actionable:** Spread loot value/spawns toward the cold zones and add reasons to visit them (objectives, better loot tiers). Metrics: route diversity, % of map area visited, time-to-first-contact, loot-per-minute spread. Check cold areas aren't simply unreachable or unreadable.
- **Why care:** Unused map is wasted level-design effort, and hotspots become predictable and repetitive.

## 2. Players almost never fight other players
- **Seen:** Only 3 `Kill` + 3 `Killed` events in 89k rows vs 2,415 bot kills; 779 of 796 matches have exactly one human. Of 445 human deaths, **91% are bots (403)**, 9% storm (39), 0.7% human. Players kill bots 5.5× more often than bots kill them (2,232 vs 403).
- **Actionable:** Revisit matchmaking/fill logic and bot difficulty (bots are too easy and are the only threat). Metrics: PvP encounters per match, player K/D vs bots, session length, retention. Caveat: the sample may be filtered or from low-population test hours.
- **Why care:** Layout choke points, sightlines and cover can't be tuned for PvP if the data shows no PvP; design for bot fights is currently what's being validated.

## 3. The storm punishes smaller maps and kills late
- **Seen:** Storm deaths are 17% of deaths on Lockdown and Grand Rift but only 5% on Ambrose Valley. They happen late (median 12:19, 10th percentile 11:26) while the median match ends at 6:22; bot deaths are median 4:17. Use *Storm deaths* heatmap: they cluster toward the map centre.
- **Actionable:** Tune storm timing/shrink speed and extraction placement on Lockdown/Grand Rift; add telegraphing for players who linger to loot in central areas. Metrics: storm-death share, extraction rate, time-to-extract, % of players alive at storm phase 2.
- **Why care:** Deaths to the storm feel unfair if caused by layout (long routes out of the centre) rather than choice.
