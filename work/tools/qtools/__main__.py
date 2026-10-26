import argparse
import json
from . import EVALUATOR_VERSION, price, validate
from .version import source_manifest

p = argparse.ArgumentParser(description='Shared exact circuit tools')
p.add_argument('command', choices=['price', 'validate', 'version'])
p.add_argument('stem', nargs='?')
p.add_argument('--processes', type=int, default=1)
p.add_argument('--no-cache', action='store_true')
args = p.parse_args()
if args.command == 'version':
    result = dict(evaluator_version=EVALUATOR_VERSION, files=source_manifest())
else:
    if args.stem is None:
        p.error('stem is required')
    result = (validate(args.stem, args.processes) if args.command == 'validate'
              else price(args.stem, args.processes, use_cache=not args.no_cache))
print(json.dumps(result, indent=2, allow_nan=False))
