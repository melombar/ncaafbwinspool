#!/usr/bin/env python3
"""
Step (b) of the a+b synthesis — reconstructed post-processor (was never committed).
Reads build/predictions_2026.json (step a = per-game Poisson-binomial, produced by
build_predictions.py) and adds, per team:
  - floor_empirical / ceiling_empirical  = market total + empirical tier band (spread_bands.json)
  - floor_p10_widened / ceiling_p90_widened = per-game roll-up widened by a season-level
      common factor (season_sigma) so the total-win SD matches the empirical sd (~2.27)
  - tier_tilt, expected_wins_widened
  - meta.synthesis block
Method documented in specs/Prediction_Model_Spec.md ("The a+b synthesis"). Governed by #22:
tilt shapes uncertainty/asymmetry, NOT expected value; level stays sum-to-market.

Run from repo root after build_predictions.py:  python3 scripts/apply_synthesis.py
"""
import json, math
import numpy as np

SEASON_SIGMA = 0.85          # common-mode factor; calibrated so total-win SD -> empirical 2.27
BANDS = json.load(open('build/spread_bands.json'))['tiers']

# PRODUCTION empirical band offsets (market_total + offset), as used by the original
# (lost) post-processor and blessed in predictions_2026. Rounded to .5, ceiling capped at
# GAMES_CAP. NOTE: these differ from spread_bands.json's raw tier stats (le4.5 -1.8/+4.3,
# 5-6.5 -3.5/+3.5, 7-8.5 -3.2/+2.0, 9+ -3.0/+2.5) — the production bands are a rounded/
# capped variant. Reconcile the two band sources; until then these reproduce the blessed file.
EMP_BANDS = {'le4.5': (-2.5, 3.5), '5-6.5': (-2.5, 2.5), '7-8.5': (-3.5, 2.5), '9+': (-2.5, 2.5)}
GAMES_CAP = 12

def rhu(x):  # round half up (original post-processor convention; market totals are all X.5)
    return int(math.floor(x + 0.5))

def tier_key(total):
    if total <= 4.5: return 'le4.5'
    if total <= 6.5: return '5-6.5'
    if total <= 8.5: return '7-8.5'
    return '9+'

def poisson_binomial(probs):
    dist = np.array([1.0])
    for p in probs:
        p = min(max(p, 1e-6), 1 - 1e-6)
        dist = np.convolve(dist, [1 - p, p])
    return dist

def widened_dist(probs):
    """Marginalise a season-level latent z ~ N(0,1): each game's logit shifted by
    SEASON_SIGMA*z (shared across the team's games -> correlated -> fatter tails)."""
    logits = [math.log(min(max(p, 1e-6), 1 - 1e-6) / (1 - min(max(p, 1e-6), 1 - 1e-6)))
              for p in probs]
    zs = np.linspace(-3.5, 3.5, 41)
    w = np.exp(-0.5 * zs**2); w /= w.sum()
    n = len(probs)
    total = np.zeros(n + 1)
    for z, wz in zip(zs, w):
        shifted = [1.0 / (1.0 + math.exp(-(l + SEASON_SIGMA * z))) for l in logits]
        total += wz * poisson_binomial(shifted)
    return total

def pctl(dist, q):
    c = 0.0
    for k, v in enumerate(dist):
        c += v
        if c >= q: return k
    return len(dist) - 1

def main():
    d = json.load(open('build/predictions_2026.json'))
    tilt_map = {}
    for team, p in d['predictions'].items():
        probs = [g['wp'] for g in p.get('per_game', [])]
        ngames = len(probs) or 12
        # total = market where present; fall back to expected_wins for the rare FCS/no-line team
        total = p.get('market_total')
        if total is None:
            total = p.get('expected_wins')
        tk = tier_key(total) if total is not None else '5-6.5'
        tilt_map[tk] = BANDS[tk]['mean']
        # empirical market+tier bands (the draft-room floor/ceiling) — production offsets
        if total is not None:
            fo, co = EMP_BANDS[tk]
            p['floor_empirical'] = max(0, rhu(total + fo))
            p['ceiling_empirical'] = min(GAMES_CAP, rhu(total + co))
        p['tier_tilt'] = BANDS[tk]['mean']
        # widened per-game roll-up (schedule-aware middle version)
        if probs:
            wd = widened_dist(probs)
            p['floor_p10_widened'] = pctl(wd, 0.10)
            p['ceiling_p90_widened'] = pctl(wd, 0.90)
            p['expected_wins_widened'] = round(float(sum(k * v for k, v in enumerate(wd))), 2)
    d['meta']['synthesis'] = {
        'season_sigma': SEASON_SIGMA,
        'tier_tilt': tilt_map,
        'note': ("Widened per-game bands (season-factor sigma %.2f -> empirical sd ~2.27) + "
                 "empirical tier-anchored floor/ceiling. Tilt shapes uncertainty/asymmetry, NOT "
                 "expected value (honest vs market efficiency #22). floor_empirical/ceiling_empirical"
                 " = market-anchored bands (draft-room floor/ceiling); floor_p10_widened/"
                 "ceiling_p90_widened = schedule-driven per-game bands. Reconstructed post-processor "
                 "(scripts/apply_synthesis.py); floor_empirical is scale-invariant." % SEASON_SIGMA),
    }
    json.dump(d, open('build/predictions_2026.json', 'w'), indent=1)
    print("synthesis applied to", len(d['predictions']), "teams")

if __name__ == '__main__':
    main()
