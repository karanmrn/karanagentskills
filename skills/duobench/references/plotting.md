# Plot customization

The default set comes from running the seed script in place:

```bash
uv run "$SKILL_DIR/scripts/plots_example.py" "$RUNS/$TS"
```

It writes `$RUNS/$TS/results/*.png` (+ `.csv`), all styled consistently
(seaborn whitegrid/talk, value labels, despined): **leaderboard**,
**cost-vs-quality** (with iso-efficiency guide lines + a color legend instead of
crowded per-dot labels), **dimensions**, **self-bias** (a *"does each judge favor
its own model?"* own-vs-other bar chart — not the old heatmap), and
**cost-breakdown** (sorted, total-cost labels).

For custom asks ("correctness vs cost only", "facet by planner", "only opus
conditions"):

```bash
cp "$SKILL_DIR/scripts/plots_example.py" "$RUNS/$TS/plots.py"
# edit $RUNS/$TS/plots.py, then:
uv run "$RUNS/$TS/plots.py" "$RUNS/$TS"
```

Notes:

- The import self-locates `plot_styles` (walks up looking for `scripts/`), so a
  copied script under the run dir needs **no** `PYTHONPATH` — but the walk-up
  only finds it when the copy lives under a tree containing the skill's
  `scripts/`. If the run dir is elsewhere, drop a copy of
  `$SKILL_DIR/scripts/plot_styles.py` next to `plots.py`.
- The `plot_styles` loaders return tidy DataFrames with dimension names read
  dynamically, so edits are small seaborn changes — never hardcode dimension
  names.
- Pitfall: don't reuse the variable name `order` for a local list — later plot
  blocks reuse the condition-order list of that name.
- Never import the removed `duobench.charts`.
- Show the user the resulting PNGs.
