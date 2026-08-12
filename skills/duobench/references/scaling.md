# Scaling to many issues/trials for statistical robustness (OPT-IN, EXPENSIVE)

**Do NOT do this by default.** The default is one issue, `--trials 1` — cheap and
fast. A single issue is an *anecdote*, not a scientific result, but multi-issue
sweeps cost real money (`issues × conditions × (planners + impl + judges) ×
trials` model jobs) and hit rate limits. Only run this when the user explicitly
asks to "make it scientific" / "run on multiple issues" / "average over runs",
and **confirm the full job count + rough cost first**.

**Two axes of replication (issues matter far more than trials):**
- **Trials per condition** (same issue) average out seed noise — LLMs vary even at
  temp 0. **3–5 trials** captures it; below 3 you can't estimate noise.
- **Distinct issues** drive generalizability and dominate the variance. Rough
  guide: **~10** issues = directional (enough for the big cost/efficiency gap),
  **~30** = defensible "scientific" (report per-condition means with 95% CIs),
  **50–100+** = strong/publishable. Tiny quality gaps (e.g. 7.5–8.5, within judge
  noise) may *never* separate — report that as the finding rather than chasing it.

**Design rules that make few issues go further:**
- **Paired/blocked:** run every condition on the *same* issue set, then compare
  *per-issue deltas* and **win-rates** ("Kimi beat Opus on $/quality on 27/30
  issues"), not just averaged means. duobench is naturally paired (all conditions
  share each issue) — exploit it; it sharply cuts the issues needed for power.
- **No selection bias:** sample a curated set across repos/difficulty (e.g. a
  SWE-bench Lite subset), don't hand-pick.

**Mechanics (no new engine code needed — reuse the per-unit flow):**
1. Run the full pipeline **once per issue** into a sibling run dir, e.g.
   `$RUNS/<ts>/issues/<owner>-<repo>-<num>/` (or one `$RUNS/<ts>__<issue>/` each).
   Each issue gets its own target clone at its own pre-fix base
   (`references/external-repo.md`). Condition ids are stable across issues, so
   they're the join key.
2. With `--trials N`, every phase job multiplies by N (`trial-0..N-1` dirs);
   `aggregate.py` already means-and-stds across a run's trials per condition.
3. **Cross-issue meta-aggregation** (small pandas step, not a model call): load
   each issue's `results.json`, group by `condition_id`, and average quality +
   cost across issues; also compute the paired win-rate per condition pair. Plot
   means with CI error bars (`cost_std`/`quality_std` × 1.96/√n) and a win-rate
   matrix. Keep per-issue `results.json` so nothing is lost.
4. Report it honestly: n (issues × trials), CIs, and which conclusions are robust
   (usually cost) vs within-noise (often quality).
