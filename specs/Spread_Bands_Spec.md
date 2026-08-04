# Empirical Spread Bands — floor/ceiling around the market total

> Replaces the model's *theoretical* (Poisson-binomial) floor/ceiling with *empirical* bands measured from 4 years of actual outcomes. Answers: how far do real teams deviate from their preseason market total, and does the deviation's shape depend on tier? Pairs with Prediction_Model_Spec.md + Pre_Pick_Doctrine.md.

## Data
343 team-seasons, 2022-2025. Preseason market total (SBD) vs actual regular-season wins (CFBD /records, FCS games included — NOT the game-file which undercounts). P4-heavy coverage; G5/thin-conf tiers underrepresented — treat exact tier numbers as approximate, shape as solid.

## The band (overall)
Actual wins land within ~**±3 of the market total**: floor(p10) −2.9, ceiling(p90) +2.9, **sd 2.27 wins**. Market is unbiased (mean +0.10; beat 49% / miss 47% / exact 4%). Your "N-win team" is realistically an N−3 to N+3 team.

## The draft-relevant asymmetry (the actual signal)
| Total tier | n | floor p10 | ceil p90 | mean resid | beat% | read |
|---|---|---|---|---|---|---|
| ≤4.5 (cheap) | 65 | −1.8 | **+4.3** | **+1.0** | 58% | fat UPSIDE tail; close floor, far ceiling |
| 5–6.5 (mid) | 110 | −3.5 | +3.5 | +0.3 | 54% | widest band, symmetric |
| 7–8.5 (good) | 117 | −3.2 | **+2.0** | **−0.5** | **38%** | TRAP: capped ceiling, tends to MISS |
| 9+ (elite) | 51 | −3.0 | +2.5 | −0.2 | 53% | holds its number |

**Shape:** value tilts UP at the bottom (cheap teams overperform, +1.0) and holds at the top (elite), and SAGS in the 7–8.5 "good but capped" middle (−0.5, only 38% beat, tightest ceiling). Backs the doctrine: upside room grows as price falls; the 7–8.5 tier is full-price for a capped, likely-to-miss outcome.

## Null result (recorded)
Within the 7–8.5 tier, preseason SP+ does NOT separate beat from miss (lower-SP+ half −0.40 vs higher-SP+ half −0.56, identical spread). SP+ is not a within-tier tiebreaker for wins — consistent with backtest #22.

## Use
- Draft-room floor/ceiling = market total + tier band (not Poisson theoretical).
- Cheap-team ceiling is genuinely high; 7–8.5 ceiling is genuinely capped — price the upside accordingly at price-equal forks (per Pre-Pick Doctrine).
