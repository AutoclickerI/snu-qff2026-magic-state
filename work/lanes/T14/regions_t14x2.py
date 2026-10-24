import sys, json, subprocess
stem = sys.argv[1]
st = json.load(open(stem + '.stage.json'))
def U(sel): return [[r['t'], r['q']] for r in st if sel(r)]
specs = {
  'only_network_noisy': U(lambda r: r['role'] not in ('net', 'tdg')),
  'only_hops_wait_noisy': U(lambda r: r['role'] != 'hop'),
  'only_encoder_noisy': U(lambda r: r['role'] != 'enc'),
  'network_and_encoder_noisy': U(lambda r: r['role'] not in ('net', 'tdg', 'enc')),
}
for name, units in specs.items():
    json.dump(dict(name=name, units=units), open(f'spec_{stem}_{name}.json', 'w'))
    out = subprocess.run(['../../../../.venv/bin/python', 'region.py', '../../T14/' + stem, f'../../T14/spec_{stem}_{name}.json', '6'],
                         cwd='../MAIN/sparse', capture_output=True, text=True)
    print(out.stdout.strip().splitlines()[-1] if out.stdout.strip() else out.stderr[-2000:], flush=True)
