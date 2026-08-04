# Apps Script proxy — setup (one time)

This gives your Draft Room HTML a single URL to fetch that returns all the sheet data as JSON, with CORS enabled — so the HTML works from a plain file on your desktop, no local server, no republish-timing issues.

## Steps

1. Open your **NCAA Wins Pool 2026** Google Sheet.
2. **Extensions → Apps Script.** A code editor opens in a new tab.
3. Delete whatever's in the default `Code.gs`, and paste the entire contents of **`wins_pool_proxy.gs`**.
4. Click **Save** (the disk icon).
5. **Deploy → New deployment.**
   - Click the gear ⚙ next to "Select type" → choose **Web app**.
   - **Description:** anything (e.g. "draft room proxy").
   - **Execute as:** **Me** (your account).
   - **Who has access:** **Anyone**.
   - Click **Deploy.**
6. It will ask you to **authorize** — click through, choose your account, "Advanced" → "Go to (project) unsafe" if warned (it's your own script), then **Allow**.
7. Copy the **Web app URL** it gives you. It ends in **`/exec`** and looks like:
   `https://script.google.com/macros/s/AKfy……/exec`
8. **Send me that /exec URL.** I'll wire the HTML to it and re-validate.

## Notes

- **"Who has access: Anyone"** means anyone with the long random URL can read the returned data (same privacy level as publish-to-web — fine for a draft board). It does NOT expose edit access.
- The script reads live from the sheet each time it's called, so the HTML always gets current data (picks, Layer B edits, everything).
- If you ever change the tab names, tell me — the script references them by name (`Dashboard (A+B join)`, `Layer A — raw data (SOURCED)`, `Layer B — pod writeups`, `Import_BradTracker`, `Draft_Order`).
- If you edit the script later, you must **Deploy → Manage deployments → edit → Deploy** again (or create a new version) for changes to take effect. The URL stays the same if you edit the existing deployment.
