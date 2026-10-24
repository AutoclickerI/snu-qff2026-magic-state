"""Region counterfactuals (channels made perfect) for a T14 build: where its loss lands."""
import sys, json, subprocess
stem = sys.argv[1]
st = json.load(open(stem + '.stage.json'))
n0 = min(r['t'] for r in st if r['role'] in ('net', 'tdg'))
EVEN = {(n0 + 1, 2), (n0 + 1, 9), (n0 + 1, 15), (n0 + 4, 7), (n0 + 4, 15), (n0 + 7, 8), (n0 + 7, 9)}
def U(sel): return [[r['t'], r['q']] for r in st if sel(r)]
specs = {
  'stage_noiseless': U(lambda r: True),
  'stage_noiseless_except_14tdg': U(lambda r: r['role'] != 'tdg'),
  'stage_noiseless_except_7even_tdg': U(lambda r: not (r['role'] == 'tdg' and (r['t'], r['q'][0]) in EVEN)),
  'encoder_noiseless': U(lambda r: r['role'] == 'enc'),
  'network_cx_noiseless': U(lambda r: r['role'] == 'net'),
  'hops_and_wait_noiseless': U(lambda r: r['role'] == 'hop'),
  'all_14tdg_noiseless': U(lambda r: r['role'] == 'tdg'),
  'even_7tdg_noiseless': U(lambda r: r['role'] == 'tdg' and (r['t'], r['q'][0]) in EVEN),
}
assert len(specs['even_7tdg_noiseless']) == 7, specs['even_7tdg_noiseless']
for name, units in specs.items():
    json.dump(dict(name=name, units=units), open(f'spec_{stem}_{name}.json', 'w'))
    out = subprocess.run(['../../../../.venv/bin/python', 'region.py', '../../T14/' + stem, f'../../T14/spec_{stem}_{name}.json', '6'],
                         cwd='../MAIN/sparse', capture_output=True, text=True)
    print(out.stdout.strip().splitlines()[-1] if out.stdout.strip() else out.stderr[-2000:], flush=True)
