"""Compare two adjoint_ablation outputs channel by channel: adjcompare.py <old.json> <new.json>."""
import json, sys
a, b = (json.load(open(p)) for p in sys.argv[1:3])
ra = {r['channel']: r for r in a['channel_ablations']}
rb = {r['channel']: r for r in b['channel_ablations']}
assert set(ra) == set(rb), 'channel sets differ'
out = dict(channels=len(ra), loss_old=a['loss'], loss_new=b['loss'], acceptance_old=a['acceptance'],
           acceptance_new=b['acceptance'], seconds_old=a['seconds'], seconds_new=b['seconds'],
           max_direct_check_error_new=b['max_direct_counterfactual_moment_error'])
for k in ('d_acceptance', 'd_unnormalized_loss', 'hypothetical_loss_reduction'):
    out['max_abs_delta_' + k] = max(abs(ra[c][k] - rb[c][k]) for c in ra)
    out['max_abs_' + k] = max(abs(ra[c][k]) for c in ra)
for n in (10, 50):
    out[f'top{n}_same_order'] = [r['channel'] for r in a['ranking'][:n]] == [r['channel'] for r in b['ranking'][:n]]
out['top10_old'] = [(r['channel'], r['hypothetical_loss_reduction']) for r in a['ranking'][:10]]
out['top10_new'] = [(r['channel'], r['hypothetical_loss_reduction']) for r in b['ranking'][:10]]
print(json.dumps(out, indent=1))
