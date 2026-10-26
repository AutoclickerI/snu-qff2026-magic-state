"""The single promotion policy in docs/reference/circuit.md."""
import math


def expected_key_delta(L_new, L_inc, t_new, t_inc):
    if not all(math.isfinite(v) for v in (L_new, L_inc, t_new, t_inc)) or min(t_new, t_inc) <= 0:
        raise ValueError('losses and times must be finite; times must be positive')
    return (L_inc - L_new) - 1.1e-7 * math.log2(t_new / t_inc)


def is_finalist(candidate, incumbent):
    """Compare validated price dictionaries; apply pairwise to select the lowest eligible L.

    Each includes raw.ok and judge.{gates_ok,seconds,shots,processes}.
    Judge timings must be measured on the same host in the same minutes.
    """
    try:
        j, old = candidate['judge'], incumbent['judge']
        return bool(
            candidate['raw']['ok'] is True and j['gates_ok'] is True
            and j['shots'] == 1_000_000 and j['processes'] == 1
            and old['shots'] == 1_000_000 and old['processes'] == 1
            and j['host'] == old['host']
            and math.isfinite(candidate['acceptance']) and candidate['acceptance'] >= .5002
            and 0 <= candidate['loss'] < incumbent['loss']
            and 0 < j['seconds'] <= 20
            and expected_key_delta(candidate['loss'], incumbent['loss'], j['seconds'], old['seconds']) > 0)
    except (KeyError, TypeError, ValueError):
        return False
