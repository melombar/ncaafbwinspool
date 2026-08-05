/**
 * Wins Pool 2026 — data proxy for the Draft Room HTML.
 * Returns Dashboard + Layer A + Layer B + picks + roster as one JSON blob, CORS-enabled.
 * Deploy: Extensions > Apps Script, paste this, Deploy > New deployment > Web app,
 *   Execute as: Me,  Who has access: Anyone.  Copy the /exec URL.
 */
function doGet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();

  function tab(name) {
    var sh = ss.getSheetByName(name);
    if (!sh) return { header: [], rows: [] };
    var values = sh.getDataRange().getValues();
    if (!values.length) return { header: [], rows: [] };
    var header = values[0].map(function (h) { return String(h).trim(); });
    var rows = [];
    for (var i = 1; i < values.length; i++) {
      var r = values[i];
      // skip fully-empty rows
      if (r.join('').trim() === '') continue;
      var obj = {};
      for (var c = 0; c < header.length; c++) obj[header[c]] = r[c];
      rows.push(obj);
    }
    return { header: header, rows: rows };
  }

  var payload = {
    ok: true,
    generated: new Date().toISOString(),
    dashboard: tab('Dashboard (A+B join)'),
    layerA:    tab('Layer A — raw data (SOURCED)'),
    layerB:    tab('Layer B — pod writeups'),
    sched:     tab('Schedule Probs'),
    picks:     tab('Import_BradTracker'),
    roster:    tab('Draft_Order')
  };

  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}
