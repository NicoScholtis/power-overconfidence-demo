"""
Build the one-page report (report/report.html -> report/report.pdf)
from analysis/results.json, so every number matches the analysis output.
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUTHOR = "Nico Scholtis"
r = json.loads((ROOT / "analysis" / "results.json").read_text())


def p(v):
    return "<i>p</i> < .001" if v < .001 else f"<i>p</i> = {v:.3f}".replace("0.", ".")


mc, oc, acc, ov = r["manipulation_check"], r["overconfidence"], r["accuracy"], r["overconfidence_overall"]
mt, ot, at = mc["test"], oc["test"], acc["test"]

html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Power and Overconfidence — demo study</title>
<style>
  @page {{ size: A4; margin: 14mm 16mm; }}
  body {{ font-family: Georgia, 'Times New Roman', serif; font-size: 10pt; line-height: 1.38; color: #222; margin: 0; }}
  h1 {{ font-size: 15pt; margin: 0 0 2px; }}
  .sub {{ color: #555; font-size: 9pt; margin-bottom: 8px; }}
  .banner {{ background: #FFF4E5; border-left: 3px solid #E67E22; padding: 5px 9px; font-size: 8.8pt; margin-bottom: 8px; }}
  h2 {{ font-size: 10.5pt; margin: 9px 0 3px; text-transform: uppercase; letter-spacing: .04em; color: #1F3A5F; }}
  p {{ margin: 0 0 5px; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; align-items: start; }}
  img {{ width: 100%; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 8.8pt; margin-top: 4px; }}
  th, td {{ border-bottom: 1px solid #ddd; padding: 2px 4px; text-align: left; }}
  th {{ color: #555; font-weight: normal; }}
  ul {{ margin: 0 0 5px 16px; padding: 0; }}
  li {{ margin-bottom: 2px; }}
  .foot {{ font-size: 8pt; color: #666; border-top: 1px solid #ddd; padding-top: 4px; margin-top: 8px; }}
</style></head><body>

<h1>Does Feeling Powerful Make Us Overconfident?</h1>
<div class="sub">A demo experiment and analysis pipeline · {AUTHOR} · October 2026</div>
<div class="banner"><b>Note:</b> this is a learning exercise. The experiment is fully functional,
but the results below come from <b>simulated data</b> (N = {r['N']}), generated to build and test the
analysis before any real data collection. They are not empirical findings.</div>

<h2>Research question</h2>
<p>Research on the psychology of power suggests that holding power changes how people perceive
themselves and others, and that overconfidence can spread and persist in groups. This demo asks a
simple question: <b>does recalling an experience of power increase overconfidence in one's own
judgments?</b></p>

<div class="grid">
<div>
<h2>Design</h2>
<ul>
  <li><b>Manipulation</b> (between-subjects): episodic recall of a time one had power over
  someone (<i>high power</i>) vs. someone had power over oneself (<i>low power</i>)
  (Galinsky, Gruenfeld &amp; Magee, 2003).</li>
  <li><b>Task:</b> 10 two-alternative general-knowledge questions, each followed by a
  confidence rating (50% = guessing, 100% = certain).</li>
  <li><b>DV:</b> overconfidence = mean confidence − % correct (in points; 0 = well calibrated).</li>
  <li><b>Checks:</b> felt power (1–7); accuracy, to rule out a knowledge difference.</li>
  <li>Built in <b>jsPsych</b> (runs in any browser); analysis in <b>Python</b>
  (pandas, SciPy), with a fixed random seed for reproducibility.</li>
</ul>
</div>
<div><img src="../figures/overconfidence_by_condition.png" alt="Overconfidence by condition"></div>
</div>

<h2>Results (simulated)</h2>
<table>
  <tr><th>Measure</th><th>High power M (SD)</th><th>Low power M (SD)</th><th>Test</th></tr>
  <tr><td>Felt power (1–7)</td><td>{mc['high_power']['mean']:.2f} ({mc['high_power']['sd']:.2f})</td>
      <td>{mc['low_power']['mean']:.2f} ({mc['low_power']['sd']:.2f})</td>
      <td><i>t</i>({mt['df']:.0f}) = {mt['t']:.2f}, {p(mt['p'])}, <i>d</i> = {mt['d']:.2f}</td></tr>
  <tr><td>Accuracy (%)</td><td>{acc['high_power']['mean']:.1f} ({acc['high_power']['sd']:.1f})</td>
      <td>{acc['low_power']['mean']:.1f} ({acc['low_power']['sd']:.1f})</td>
      <td><i>t</i>({at['df']:.0f}) = {at['t']:.2f}, {p(at['p'])}</td></tr>
  <tr><td><b>Overconfidence (pts)</b></td><td><b>{oc['high_power']['mean']:.1f}</b> ({oc['high_power']['sd']:.1f})</td>
      <td><b>{oc['low_power']['mean']:.1f}</b> ({oc['low_power']['sd']:.1f})</td>
      <td><i>t</i>({ot['df']:.0f}) = {ot['t']:.2f}, {p(ot['p'])}, <i>d</i> = {ot['d']:.2f}</td></tr>
</table>
<p style="margin-top:5px">The manipulation check worked, and there was no evidence of an accuracy difference between conditions.
Participants were overconfident overall (M = {ov['mean']:.1f} pts, <i>t</i>({ov['df']}) = {ov['t']:.2f}, {p(ov['p'])}),
and those in the high-power condition were more overconfident (difference = {ot['diff']:.1f} pts,
95% CI [{ot['ci_low']:.1f}, {ot['ci_high']:.1f}], Welch's <i>t</i>-test). Because the data are simulated,
these numbers only show that the pipeline works end to end.</p>

<div class="grid">
<div>
<h2>Limitations &amp; next steps</h2>
<ul>
  <li>The simulation assumed a small true effect (5 confidence points, <i>d</i> ≈ 0.23). With 60 per
  condition, a Monte Carlo check shows only ~24% power, so the significant result here is partly a
  lucky draw. A real study would need ≈ 290 per condition for 80% power, and a pre-registered
  sample size.</li>
  <li>Recall manipulations can be weak online; consider attention and writing-quality checks.</li>
  <li>Possible extension: a social condition to test whether overconfidence spreads from
  high-power partners.</li>
</ul>
</div>
<div>
<h2>How I used Claude Code</h2>
<ul>
  <li>I described the study in plain language; Claude Code wrote the jsPsych experiment,
  the simulation and the analysis scripts.</li>
  <li>I ran the experiment myself as a participant, checked the data and figures, and asked
  Claude to justify each statistical choice (e.g., Welch vs. Student's <i>t</i>).</li>
  <li>Takeaway: AI agents can greatly speed up lab work, but the researcher must still
  check the design, the code and the interpretation.</li>
</ul>
</div>
</div>

<div class="foot">Materials: experiment (<code>experiment/index.html</code>), simulation and analysis
scripts (<code>analysis/</code>), data (<code>data/</code>). Reference: Galinsky, A. D., Gruenfeld, D. H.,
&amp; Magee, J. C. (2003). From power to action. <i>JPSP, 85</i>(3), 453–466.</div>
</body></html>"""

out_html = ROOT / "report" / "report.html"
out_html.write_text(html, encoding="utf-8")

chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={ROOT / 'report' / 'report.pdf'}", out_html.as_uri()],
               check=True, capture_output=True)
print("Report saved to report/report.pdf")
