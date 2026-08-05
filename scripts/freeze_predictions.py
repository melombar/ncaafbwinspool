"""Freeze predictions_YYYY.json at draft time — the permanent record.

WHY THIS IS A SCRIPT, NOT A MANUAL EDIT:
Per Prediction_Model_Spec.md, the frozen file is the ONLY admissible validation
record: "A prediction not recorded before kickoff is not admissible." Freezing must
be (1) done exactly once, (2) at draft, (3) immutable afterward, (4) content-hashed
so a later edit is detectable. Run this the moment the draft board is locked.

DO NOT run before draft. Before draft the model still moves (wk1-4 lines keep
posting, an August SP+ refresh may land, the 9.4-vs-14 curve-scale flag may resolve).
Freezing early locks a non-final record and defeats the one-shot backtest.

Usage:
    python scripts/freeze_predictions.py            # dry-run: report status, no write
    python scripts/freeze_predictions.py --commit   # flip frozen:true + snapshot
"""
import json, sys, hashlib, datetime, os

PRED = os.path.join(os.path.dirname(__file__), '..', 'build', 'predictions_2026.json')
YEAR = 2026

def content_hash(preds_obj):
    # hash the predictions payload only (not meta), so the freeze stamp itself
    # doesn't change the hash it certifies.
    payload = json.dumps(preds_obj['predictions'], sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(payload.encode()).hexdigest()

def main():
    commit = '--commit' in sys.argv
    d = json.load(open(PRED))
    meta = d['meta']
    if meta.get('frozen'):
        print(f"ALREADY FROZEN at {meta.get('frozen_at')} (hash {meta.get('frozen_hash','?')[:12]}). No action.")
        return
    h = content_hash(d)
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    print(f"predictions: {len(d['predictions'])} teams")
    print(f"content hash: {h}")
    if not commit:
        print("DRY RUN — not frozen. Re-run with --commit AT DRAFT TIME to lock.")
        return
    meta['frozen'] = True
    meta['frozen_at'] = ts
    meta['frozen_hash'] = h
    json.dump(d, open(PRED, 'w'), indent=1)
    snap = os.path.join(os.path.dirname(PRED), f'predictions_{YEAR}_FROZEN_{ts[:10]}.json')
    json.dump(d, open(snap, 'w'), indent=1)
    print(f"FROZEN at {ts}")
    print(f"snapshot: {os.path.basename(snap)}")
    print("Commit both files to the repo now. This is the permanent record.")

if __name__ == '__main__':
    main()
