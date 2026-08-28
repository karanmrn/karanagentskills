/**
 * Tier-alignment invariant (free, static).
 *
 * Kills the "inert demotion" defect class: E2E_TIERS declares a test's tier,
 * but the paid test files also self-gate on `process.env.EVALS_TIER === '<tier>'`.
 * When the two disagree, the touchfiles declaration is dead metadata — the
 * #2077 demotion of the plan-mode/finding-floor smokes to 'periodic' was inert
 * for months because the files still gated on 'gate' and ran in the blocking
 * lane on every gate run.
 *
 * Mapping rule (test filenames do NOT map mechanically to tier keys): for each
 * `test/skill-e2e-*.test.ts` with an EVALS_TIER self-gate, search the
 * E2E_TOUCHFILES / LLM_JUDGE_TOUCHFILES dep lists for the exact file path. If
 * found under key K, the file's self-gate tier must equal E2E_TIERS[K]. Files
 * not named in any dep list are REPORTED as unmapped (a nudge to add them to
 * their eval's dep list), never silently skipped.
 */

import { describe, test, expect } from 'bun:test';
import { readdirSync, readFileSync } from 'fs';
import * as path from 'path';
import { E2E_TOUCHFILES, E2E_TIERS, LLM_JUDGE_TOUCHFILES } from './helpers/touchfiles';

const TEST_DIR = import.meta.dir;
// Both quote styles — a mechanical refactor to double quotes must not
// silently drop a file from the invariant (fail-open is the defect class
// this test exists to kill).
const SELF_GATE_RE = /EVALS_TIER\s*===\s*['"](gate|periodic)['"]/g;

describe('E2E tier alignment (touchfiles declaration vs test self-gate)', () => {
  const testFiles = readdirSync(TEST_DIR)
    .filter((f) => f.startsWith('skill-e2e-') && f.endsWith('.test.ts'))
    .sort();

  const allDeps: Record<string, string[]> = { ...E2E_TOUCHFILES, ...LLM_JUDGE_TOUCHFILES };

  test('every self-gated test file named in a dep list matches its declared tier', () => {
    const misaligned: string[] = [];
    const reported: string[] = [];

    for (const file of testFiles) {
      const content = readFileSync(path.join(TEST_DIR, file), 'utf-8');
      const tiers = new Set<string>();
      for (const m of content.matchAll(SELF_GATE_RE)) tiers.add(m[1]);
      const repoPath = `test/${file}`;
      if (tiers.size === 0) {
        // Every skill-e2e file is expected to self-gate; zero matches means
        // either a genuinely ungated file or a gate shape the regex can't
        // see — both worth a visible report, never a silent skip.
        reported.push(`${repoPath}: no detectable EVALS_TIER self-gate`);
        continue;
      }
      if (tiers.size > 1) {
        reported.push(`${repoPath}: mixed-tier self-gates (${[...tiers].join(', ')}) — not tier-checked`);
        continue;
      }
      const selfTier = [...tiers][0];

      const owningKeys = Object.keys(allDeps).filter((k) => allDeps[k].includes(repoPath));
      if (owningKeys.length === 0) {
        reported.push(`${repoPath} (self-gates '${selfTier}'): not named in any touchfiles dep list`);
        continue;
      }
      for (const k of owningKeys) {
        const declared = E2E_TIERS[k];
        if (!declared) {
          // A dep-list key with no E2E_TIERS entry (e.g. an LLM-judge key)
          // can't tier-check this file — report instead of silently passing.
          reported.push(`${repoPath}: matched key '${k}' which has no E2E_TIERS entry`);
          continue;
        }
        if (declared !== selfTier) {
          misaligned.push(
            `${repoPath}: self-gates on '${selfTier}' but E2E_TIERS['${k}'] declares '${declared}' — the declaration is inert`,
          );
        }
      }
    }

    // Reported, not asserted: coverage holes the invariant can see but not
    // arbitrate. Add the test file to its eval's dep list (or a tier entry
    // for the key) to bring it under the invariant.
    if (reported.length > 0) {
      console.warn(
        `[tier-alignment] ${reported.length} file(s) outside the invariant:\n  ` + reported.join('\n  '),
      );
    }

    expect(misaligned).toEqual([]);
  });
});
