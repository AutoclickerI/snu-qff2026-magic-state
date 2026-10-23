"""Submit to / query the QFF2026 hackathon site (Supabase RPCs the site's own JS uses).

    python submit.py submit submissions/<name>.qasm submissions/<name>.json
    python submit.py status          # my recent submissions (status, score, message)
    python submit.py wait            # seconds until the next submission is accepted (-1: unknown/pending)
    python submit.py board           # public leaderboard

Credentials come from ../.submit_credentials (TEAM=..., PASSWORD=...), never printed.
"""
import json
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
URL = "https://ezebbyoxohgouodwvbfv.supabase.co"
# The public "anon" key shipped in the site's assets/supabase-config.js (designed to be public).
ANON = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV6ZWJieW94b2hnb3VvZHd2YmZ2Iiwi"
        "cm9sZSI6ImFub24iLCJpYXQiOjE3OTAzMTg4MjEsImV4cCI6MjEwNTg5NDgyMX0.WfLKHLMDpRjaKkFhbi_pGpN215pCxl4jZK3md55kIsE")


def creds():
    kv = {}
    for line in (ROOT / ".submit_credentials").read_text(encoding="utf-8").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip()
    return kv["TEAM"], kv["PASSWORD"]


def call(path, payload=None, method="POST"):
    req = urllib.request.Request(URL + path, method=method,
                                 data=None if payload is None else json.dumps(payload).encode(),
                                 headers={"apikey": ANON, "Authorization": f"Bearer {ANON}",
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")


def main():
    cmd = sys.argv[1]
    if cmd == "board":
        st, rows = call("/rest/v1/qff_leaderboard?select=team_name,score_a,score_key,n_2q,p_acc,submitted_at"
                        "&order=score_key.asc,n_2q.asc,submitted_at.asc", method="GET")
        for i, r in enumerate(rows, 1):
            print(f"{i:2d}. {r['team_name']:<16} 1-F={r['score_a']:.4g} (key {r['score_key']})  2q={r['n_2q']}"
                  f"  acc={r['p_acc']:.3f}  {r['submitted_at']}")
        return
    team, pw = creds()
    if cmd == "status":
        st, rows = call("/rest/v1/rpc/team_submissions", {"p_team_name": team, "p_password": pw})
        print(st, json.dumps(rows, indent=1, ensure_ascii=False)[:4000])
        st, nxt = call("/rest/v1/rpc/team_next_submission", {"p_team_name": team, "p_password": pw})
        print("next:", st, nxt)
    elif cmd == "wait":  # seconds until the server accepts our next submission
        st, nxt = call("/rest/v1/rpc/team_next_submission", {"p_team_name": team, "p_password": pw})
        print(nxt[0]["wait_seconds"] if st == 200 and not nxt[0]["pending"] else -1)
    elif cmd == "submit":
        qasm = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8").strip()
        dq = json.loads(pathlib.Path(sys.argv[3]).read_text())["data_qubits"]
        assert len(qasm.encode()) <= 200_000 and len(set(dq)) == 7
        st, res = call("/rest/v1/rpc/submit_solution",
                       {"p_team_name": team, "p_password": pw, "p_qasm": qasm, "p_data_qubits": dq})
        print(st, res)


if __name__ == "__main__":
    main()
