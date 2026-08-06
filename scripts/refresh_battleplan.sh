#!/usr/bin/env bash
# Refresh the Wins Pool battle plan after new BBOC pods load.
# Overwrites build/mc_paths_2026.json + almanac/battle_plan_2026.html IN PLACE (discards prior version).
# The Layer-B scorer globs almanac/bboc_2026_*.json, so newly-added pods are picked up automatically.
set -e
cd "$(dirname "$0")/.."
echo "→ Monte Carlo (season + draft tournament, β-sensitivity)…"
python3 scripts/monte_carlo_draft.py
echo "→ Rendering battle_plan_2026.html…"
python3 scripts/gen_battleplan.py
echo "✓ Refreshed. Deliver almanac/battle_plan_2026.html + update the 'wins-pool-2026-battle-plan' artifact in place."
