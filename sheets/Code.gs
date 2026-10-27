/**
 * Support Team Lead Kit for Google Sheets.
 *
 * Install: open a blank Google Sheet, Extensions > Apps Script, paste this file, save,
 * reload the sheet, then use the "Lead Kit" menu > "Set up workbook".
 *
 * Creates four tabs:
 *   Scorecard   criteria, weights and auto fail flags (edit here, everything else follows)
 *   Reviews     one row per reviewed ticket, 0/1/2 per criterion, score computed by formula
 *   Agents      per agent average, pass rate and auto fail count (formulas)
 *   Calibration paste the calibration round here, bias and spread computed by formula
 */

var CRITERIA = [
  // id, category, text, weight, auto fail
  ['correct_info', 'Accuracy', 'Information correct and complete', 15, true],
  ['resolved', 'Accuracy', 'Resolved or clear next step and date', 12, false],
  ['policy', 'Accuracy', 'Policy and process followed', 8, true],
  ['clarity', 'Communication', 'Easy to follow, ordered steps', 10, false],
  ['tone', 'Communication', 'Tone matches customer and brand', 10, false],
  ['language', 'Communication', 'Grammar, spelling, formatting', 10, false],
  ['first_contact', 'Efficiency', 'Everything handled in one reply', 10, false],
  ['internal_notes', 'Efficiency', 'Notes, tags, macros correct', 10, false],
  ['acknowledge', 'Empathy', 'Situation acknowledged specifically', 8, false],
  ['ownership', 'Empathy', 'Agent owns the problem', 7, false]
];
var PASS_THRESHOLD = 85;
var TOLERANCE = 5;

function onOpen() {
  SpreadsheetApp.getUi().createMenu('Lead Kit')
    .addItem('Set up workbook', 'setupWorkbook')
    .addToUi();
}

function getOrCreate_(ss, name) {
  var sh = ss.getSheetByName(name);
  if (!sh) sh = ss.insertSheet(name);
  sh.clear();
  return sh;
}

function setupWorkbook() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var n = CRITERIA.length;

  // Scorecard tab
  var sc = getOrCreate_(ss, 'Scorecard');
  sc.getRange(1, 1, 1, 5).setValues([['id', 'category', 'criterion', 'weight', 'auto_fail']]).setFontWeight('bold');
  sc.getRange(2, 1, n, 5).setValues(CRITERIA);
  sc.getRange(n + 3, 1, 1, 2).setValues([['pass_threshold', PASS_THRESHOLD]]);
  sc.getRange(n + 4, 1, 1, 2).setValues([['weights_total', '=SUM(D2:D' + (n + 1) + ')']]);
  sc.setFrozenRows(1);

  // Reviews tab
  var rv = getOrCreate_(ss, 'Reviews');
  var header = ['ticket_id', 'agent', 'evaluator', 'date'].concat(CRITERIA.map(function (c) { return c[0]; }))
    .concat(['raw_score', 'auto_fail', 'score', 'passed', 'comment']);
  rv.getRange(1, 1, 1, header.length).setValues([header]).setFontWeight('bold');
  var firstCrit = 5, lastCrit = 4 + n;
  var colRaw = lastCrit + 1, colAF = lastCrit + 2, colScore = lastCrit + 3, colPass = lastCrit + 4;
  var L = function (c) { return columnLetter_(c); };
  var critRange = L(firstCrit) + '2:' + L(lastCrit) + '2';
  // raw = SUMPRODUCT(values/2, weights)
  var rawF = '=IF(COUNTA(' + critRange + ')<' + n + ',"",SUMPRODUCT(' + critRange + '/2,TRANSPOSE(Scorecard!$D$2:$D$' + (n + 1) + ')))';
  var afF = '=IF(' + L(colRaw) + '2="","",SUMPRODUCT((' + critRange + '=0)*TRANSPOSE(Scorecard!$E$2:$E$' + (n + 1) + '))>0)';
  var scoreF = '=IF(' + L(colRaw) + '2="","",IF(' + L(colAF) + '2,0,' + L(colRaw) + '2))';
  var passF = '=IF(' + L(colScore) + '2="","",' + L(colScore) + '2>=Scorecard!$B$' + (n + 3) + ')';
  var rows = 500;
  rv.getRange(2, colRaw, rows, 1).setFormula(rawF);
  rv.getRange(2, colAF, rows, 1).setFormula(afF);
  rv.getRange(2, colScore, rows, 1).setFormula(scoreF);
  rv.getRange(2, colPass, rows, 1).setFormula(passF);
  var rule = SpreadsheetApp.newDataValidation().requireValueInList(['0', '1', '2'], true).setAllowInvalid(false).build();
  rv.getRange(2, firstCrit, rows, n).setDataValidation(rule);
  rv.setFrozenRows(1);
  rv.setFrozenColumns(2);

  // Agents tab
  var ag = getOrCreate_(ss, 'Agents');
  ag.getRange(1, 1, 1, 5).setValues([['agent', 'reviews', 'avg_score', 'pass_rate', 'auto_fails']]).setFontWeight('bold');
  ag.getRange('A2').setFormula('=SORT(UNIQUE(FILTER(Reviews!B2:B, Reviews!B2:B<>"")))');
  var sCol = L(colScore), pCol = L(colPass), aCol = L(colAF);
  ag.getRange(2, 2, 100, 1).setFormula('=IF(A2="","",COUNTIFS(Reviews!$B:$B,A2,Reviews!$' + sCol + ':$' + sCol + ',"<>"))');
  ag.getRange(2, 3, 100, 1).setFormula('=IF(A2="","",ROUND(AVERAGEIFS(Reviews!$' + sCol + ':$' + sCol + ',Reviews!$B:$B,A2),1))');
  ag.getRange(2, 4, 100, 1).setFormula('=IF(A2="","",ROUND(100*COUNTIFS(Reviews!$B:$B,A2,Reviews!$' + pCol + ':$' + pCol + ',TRUE)/B2,1))');
  ag.getRange(2, 5, 100, 1).setFormula('=IF(A2="","",COUNTIFS(Reviews!$B:$B,A2,Reviews!$' + aCol + ':$' + aCol + ',TRUE))');
  ag.setFrozenRows(1);

  // Calibration tab
  var cb = getOrCreate_(ss, 'Calibration');
  cb.getRange(1, 1, 1, 6).setValues([['ticket_id', 'evaluator', 'score', 'consensus', 'deviation', 'within_tol']]).setFontWeight('bold');
  cb.getRange(2, 4, 300, 1).setFormula('=IF(A2="","",MEDIAN(FILTER($C$2:$C,$A$2:$A=A2)))');
  cb.getRange(2, 5, 300, 1).setFormula('=IF(A2="","",C2-D2)');
  cb.getRange(2, 6, 300, 1).setFormula('=IF(A2="","",ABS(E2)<=' + TOLERANCE + ')');
  cb.getRange('H1:K1').setValues([['evaluator', 'bias', 'mean_abs_dev', 'within_tol_pct']]).setFontWeight('bold');
  cb.getRange('H2').setFormula('=SORT(UNIQUE(FILTER(B2:B,B2:B<>"")))');
  cb.getRange(2, 9, 50, 1).setFormula('=IF(H2="","",ROUND(AVERAGEIF($B$2:$B,H2,$E$2:$E),1))');
  cb.getRange(2, 10, 50, 1).setFormula('=IF(H2="","",ROUND(AVERAGE(ARRAYFORMULA(ABS(FILTER($E$2:$E,$B$2:$B=H2)))),1))');
  cb.getRange(2, 11, 50, 1).setFormula('=IF(H2="","",ROUND(100*COUNTIFS($B$2:$B,H2,$F$2:$F,TRUE)/COUNTIF($B$2:$B,H2),1))');
  cb.getRange('M1:N1').setValues([['overall_within_tol_pct', 'tickets_spread_gt_2tol']]).setFontWeight('bold');
  cb.getRange('M2').setFormula('=IFERROR(ROUND(100*COUNTIF(F2:F,TRUE)/COUNTA(A2:A),1),"")');
  cb.getRange('N2').setFormula('=IFERROR(SUMPRODUCT((MAXIFS(C2:C,A2:A,UNIQUE(FILTER(A2:A,A2:A<>"")))-MINIFS(C2:C,A2:A,UNIQUE(FILTER(A2:A,A2:A<>""))))>' + (2 * TOLERANCE) + '),"")');
  cb.setFrozenRows(1);

  var def = ss.getSheetByName('Sheet1');
  if (def && ss.getSheets().length > 1) ss.deleteSheet(def);
  SpreadsheetApp.getUi().alert('Lead Kit workbook ready. Edit weights in Scorecard, log reviews in Reviews.');
}

function columnLetter_(col) {
  var s = '';
  while (col > 0) { var m = (col - 1) % 26; s = String.fromCharCode(65 + m) + s; col = (col - m - 1) / 26; }
  return s;
}
