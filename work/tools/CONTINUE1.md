# TOOLS continuation (main session, 2026-10-26 16:40)
Answer: my 1e-15 relative criterion was too strict; a different contraction order changes roundoff. Tests enforce
|L_warm - L_cold| <= 1e-15 absolute and |A_warm - A_cold| <= 1e-12 absolute (both far below the 1e-10-scale gains the
search acts on); record the observed differences in REPORT.md. Continue to completion of the brief without stopping
for questions: decide technical choices yourself, record each decision and its reason in REPORT.md, and keep going.
Remember the SSH correction (plain ssh -q, no ControlMaster=no) for pin_hosts.py.
