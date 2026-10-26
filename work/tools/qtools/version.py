"""Content-address every Python source that can affect shared evaluation."""
import hashlib
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
TOOLS = PACKAGE.parent


def source_manifest(package=PACKAGE):
    package = Path(package)
    return {str(p.relative_to(package)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(package.rglob('*.py'))}


def evaluator_version(package=PACKAGE):
    h = hashlib.sha256()
    for name, digest in source_manifest(package).items():
        h.update(name.encode() + b'\0' + bytes.fromhex(digest))
    return h.hexdigest()


EVALUATOR_VERSION = evaluator_version()
